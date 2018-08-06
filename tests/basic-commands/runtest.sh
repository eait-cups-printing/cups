#!/bin/bash
# runtest.sh - basic commands
# Author: Yulia Kopkova <ykopkova@redhat.com>
# Location: /CoreOS/cups/Sanity/basic_commands/Makefile

# Description: Test for basic CUPS commands

# Copyright (c) 2008 Red Hat, Inc. This copyrighted material
# is made available to anyone wishing to use, modify, copy, or
# redistribute it subject to the terms and conditions of the GNU General

# Public License v.2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# Include Beaker environment
. /usr/bin/rhts-environment.sh
. /usr/share/beakerlib/beakerlib.sh

PACKAGE=cups

FILEPDF=testfile.pdf
FILEJPG=testfile.jpg
NUMJOBS=50
TIMEOUT=30
TPRN1="testprinter1"
TPRN2="testprinter2"
FILEDEV="FileDevice YES"
CUPSCONF=/etc/cups/cupsd.conf
if `rlIsRHEL 5` ; then
   ML="postscript.ppd.gz"
else
    ML="drv:///sample.drv/deskjet.ppd"
fi

function setCupsCtlFileDeviceConf {
if `rlIsRHEL 5 6`;then
    echo 'FileDevice YES' >> /etc/cups/cupsd.conf
else
    echo 'FileDevice YES' >> /etc/cups/cups-files.conf
fi
}

rlJournalStart
    rlPhaseStartSetup
        
        rlAssertRpm $PACKAGE
        rlFileBackup --clean "/etc/cups" "/etc/printcap"

        rlServiceStop cups
        rlFileBackup $CUPSCONF /etc/cups/cups-files.conf
        rlRun "setCupsCtlFileDeviceConf"
        rlServiceStart cups

    rlPhaseEnd

    rlPhaseStartTest

        rlRun "lpadmin -p $TPRN1 -v file:/dev/null -E -m $ML" 0 "Create printer $TPRN1"
        rlRun "lpadmin -d $TPRN1" 0 "Set $TPRN1 default" 
        rlRun "lpadmin -p $TPRN2 -v file:/dev/null -E -m $ML" 0 "Create printer $TPRN2"

        rlRun "lp $FILEPDF" 0 "Print $FILEPDF with lp and default printer" 
        rlRun "lp -d $TPRN2 $FILEJPG" 0 "Print $FILEJPG with lp and $TPRN2"
        rlRun "lp -d $TPRN1 -P 1-2 -o job-sheets=classified,classified $FILEPDF" 0 "Print $FILEPDF with lp and $TPRN1"

        for ((i=0; i < $NUMJOBS; i++)); do
            lp -d $TPRN1 $FILEJPG &
            sleep 0.02s
            lp -d $TPRN2 $FILEJPG &
            sleep 0.02s
            lppid=$!
        done

        rlRun "wait $lppid" 0 "$NUMJOBS jobs queued"

        for ((i=$TIMEOUT; i>0; i-=5 )); do
            jobs=$(lpstat)
            [ "x$jobs" = "x" ] && break
            sleep 5
        done

        rlRun "lpr $FILEPDF" 0 "Print $FILEPDF with lpr and default printer"
        rlRun "lpr -P $TPRN2 $FILEJPG" 0 "Print $FILEJPG with lpr and $TPRN2"
        rlRun "lpr -P $TPRN1 -o number-up=2 -o job-sheets=standard,none $FILEPDF" 0 "Print $FILEPDF with lpr and $TPRN1"

        for ((i=0; i < $NUMJOBS ; i++)); do
            lpr -P $TPRN1 $FILEJPG &
            sleep 0.02s
            lpr -P $TPRN2 $FILEJPG &
            sleep 0.02s
            lprpid=$!
        done

        rlRun "wait $lprpid" 0 "$NUMJOBS jobs queued"

        for ((i=$TIMEOUT; i>0 ; i-=5)); do
            jobs=$(lpstat)
            [ "x$jobs" = "x" ] && break
            sleep 5
        done

        job_id=$(lp -d $TPRN1 -o job-hold-until=indefinite $FILEJPG | awk '{ match($0, /testprinter1-([0-9]+)/, arr); print arr[1] }')
        rlRun "cancel $TPRN1-$job_id" 0 "Cancel $TPRN1-$job_id job"
        rlRun "lp -d $TPRN1 -o job-hold-until=indefinite $FILEJPG" 0 "Hold job on $TPRN1"
        rlRun "lp -d $TPRN2 -o job-hold-until=indefinite $FILEJPG" 0 "Hold job on $TPRN2"
        rlRun "cancel -a" 0 "Cancel all jobs"
        
        rlRun "lpc status" 0 "Show printers status" 

        rlRun "lpq" 0 "Show printer queue status" 

        rlRun "lpstat -t" 0 "Show all status information"

        rlRun "lpinfo -m" 0 "Show list of available drivers"

        rlRun "lpinfo -v" 0 "Show list of available devices"

        rlRun "lpr -o job-hold-until=indefinite $FILEJPG" 0 "Hold test file"
        rlRun "lprm" 0 "Cancel current job on default printer"
        
        rlRun "lpr -P $TPRN1 -o job-hold-until=indefinite $FILEJPG" 0 "Hold test file"
        rlRun "lprm $TPRN1" 0 "Cancel current job on $TPRN1"
        
        rlRun "lpadmin -p $TPRN1 -v file:/tmp/$TPRN1 -o PageSize=A4" 0 "Modify $TPRN1"

        rlRun "lpadmin -x $TPRN1" 0 "Delete $TPRN1"
        rlRun "lpadmin -x $TPRN2" 0 "Delete $TPRN2"


    rlPhaseEnd

    rlPhaseStartCleanup
        rlServiceStop cups 
        rlRun "rm -f $CUPSCONF" 0 "Remove modified cupsd.conf"
        rlFileRestore
        rlServiceRestore cups

    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
