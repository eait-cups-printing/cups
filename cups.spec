%define initdir /etc/rc.d/init.d
%define use_alternatives 1
%define use_dbus 1
%define build_as_pie 1

Summary: Common Unix Printing System
Name: cups
Version: 1.1.23
Release: 14
License: GPL
Group: System Environment/Daemons
Source: ftp://ftp.easysw.com/pub/cups/test/cups-%{version}-source.tar.bz2
Source1: cups.init
Source2: cupsprinter.png
Source5: cups-lpd
Source6: pstoraster
Source7: pstoraster.convs
Source8: postscript.ppd.gz
Source9: cups.logrotate
Source10: ncp.backend
Source11: cups.conf
Source12: cups.cron
Patch0: cups-1.1.15-initscript.patch
Patch1: cups-1.1.14-doclink.patch
Patch2: cups-1.1.16-system-auth.patch
Patch3: cups-1.1.17-backend.patch
Patch4: cups-ext.patch
Patch5: cups-str1023.patch
Patch6: cups-1.1.17-pdftops.patch
Patch7: cups-logfileperm.patch
Patch8: cups-1.1.17-rcp.patch
Patch9: cups-1.1.17-ppdsdat.patch
Patch10: cups-1.1.17-sanity.patch
Patch11: cups-1.1.19-lpstat.patch
Patch12: cups-locale.patch
Patch13: cups-CAN-2005-0064.patch
Patch14: cups-str1068.patch
Patch15: cups-sigchld.patch
Patch16: cups-pie.patch
Patch17: cups-1.1.19-no_rpath.patch
Patch18: cups-language.patch
Patch19: cups-gcc34.patch
Patch20: cups-gcc4.patch
Patch24: cups-maxlogsize.patch
Patch25: cups-enabledisable.patch
Patch28: cups-no-propagate-ipp-port.patch
Patch30: cups-session-printing.patch
Patch32: cups-pid.patch
Patch33: cups-CAN-2004-0888.patch
Patch34: cups-dbus.patch
Epoch: 1
Url: http://www.cups.org/
BuildRoot: %{_tmppath}/%{name}-root
PreReq: /sbin/chkconfig /sbin/service
Requires: %{name}-libs = %{epoch}:%{version}
%if %use_alternatives
Provides: /usr/bin/lpq /usr/bin/lpr /usr/bin/lp /usr/bin/cancel /usr/bin/lprm /usr/bin/lpstat
Prereq: /usr/sbin/alternatives
%endif

# Unconditionally obsolete LPRng so that upgrades work properly.
Obsoletes: lpd lpr LPRng <= 3.8.15-3
Provides: lpd lpr LPRng = 3.8.15-3

BuildPrereq: pam-devel openssl-devel pkgconfig
BuildRequires: make >= 1:3.80
%if %use_dbus
BuildPrereq: dbus-devel = 0.31
Requires: dbus = 0.31
%endif

%package devel
Summary: Common Unix Printing System - development environment
Group: Development/Libraries
Requires: %{name}-libs = %{epoch}:%{version}
Requires: openssl-devel

%package libs
Summary: Common Unix Printing System - libraries
Group: System Environment/Libraries

%package lpd
Summary: Common Unix Printing System - lpd emulation
Group: System Environment/Daemons
Requires: %{name} = %{epoch}:%{version} xinetd

%description
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. It has been developed by Easy Software Products 
to promote a standard printing solution for all UNIX vendors and users. 
CUPS provides the System V and Berkeley command-line interfaces. 

%description devel
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. This is the development package for creating
additional printer drivers, and other CUPS services.

%description libs
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. It has been developed by Easy Software Products 
to promote a standard printing solution for all UNIX vendors and users. 
CUPS provides the System V and Berkeley command-line interfaces. 
The cups-libs package provides libraries used by applications to use CUPS
natively, without needing the lp/lpr commands.

%description lpd
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. This is the package that provices standard 
lpd emulation.

%prep
%setup -q
%patch0 -p1 -b .noinit
%patch1 -p1 -b .doclink
%patch2 -p1 -b .system-auth
%patch3 -p1 -b .backend
%patch4 -p1 -b .ext
%patch5 -p1 -b .str1023
%patch6 -p1 -b .pdftops
%patch7 -p1 -b .logfileperm
%patch8 -p1 -b .rcp
%patch9 -p1 -b .ppdsdat
%patch10 -p1 -b .sanity
%patch11 -p1 -b .lpstat
%patch12 -p1 -b .locale
%patch13 -p1 -b .CAN-2005-0064
%patch14 -p1 -b .str1068
%patch15 -p1 -b .sigchld
%if %build_as_pie
%patch16 -p1 -b .pie
%endif
%patch17 -p1 -b .no_rpath
%patch18 -p1 -b .language
%patch19 -p1 -b .gcc34
%patch20 -p1 -b .gcc4
%patch24 -p1 -b .maxlogsize
%patch25 -p1 -b .enabledisable
%patch28 -p1 -b .no-propagate-ipp-port
#%patch30 -p1 -b .session-printing
%patch32 -p1 -b .pid
%patch33 -p1 -b .CAN-2004-0888
%if %use_dbus
%patch34 -p1 -b .dbus
%endif
perl -pi -e 's,^#(Printcap\s+/etc/printcap),$1,' conf/cupsd.conf.in
aclocal -I config-scripts
autoconf

cp %{SOURCE5} cups-lpd.real
perl -pi -e "s,\@LIBDIR\@,%{_libdir},g" cups-lpd.real

# Let's look at the compilation command lines.
perl -pi -e "s,^.SILENT:,," Makedefs.in

for i in man/{es,fr}/*.man templates/{de,fr}/*.tmpl; do
	iconv -f iso-8859-1 -t utf-8 < "$i" > "${i}_"
	mv "${i}_" "$i"
done

%build
if pkg-config openssl ; then
  export CFLAGS=`pkg-config --cflags openssl`
  export CPPFLAGS=`pkg-config --cflags-only-I openssl`
  export LDFLAGS=`pkg-config --libs-only-L openssl`
fi
%configure --with-docdir=%{_docdir}/cups-%{version} \
	--with-optim="$RPM_OPT_FLAGS $CFLAGS"

# If we got this far, all prerequisite libraries must be here.
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{initdir}

make BUILDROOT=$RPM_BUILD_ROOT install 

install -m 755 $RPM_SOURCE_DIR/cups.init $RPM_BUILD_ROOT%{initdir}/cups

find $RPM_BUILD_ROOT/usr/share/cups/model -name "*.ppd" |xargs gzip -n9f

%if %use_alternatives
pushd $RPM_BUILD_ROOT%{_bindir}
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i $i.cups
done
cd $RPM_BUILD_ROOT%{_sbindir}
mv lpc lpc.cups
cd $RPM_BUILD_ROOT%{_mandir}/man1
for i in lp lpq lpr lprm lpstat; do
	mv $i.1 $i-cups.1
done
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/cancel.1
ln -s lp-cups.1 $RPM_BUILD_ROOT%{_mandir}/man1/cancel-cups.1
cd $RPM_BUILD_ROOT%{_mandir}/man8
mv lpc.8 lpc-cups.8
popd
%endif

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps $RPM_BUILD_ROOT%{_sysconfdir}/X11/sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/System $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily
install -c -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -c -m 644 cups-lpd.real $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d/cups-lpd
install -c -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/cups
install -c -m 755 %{SOURCE10} $RPM_BUILD_ROOT%{_libdir}/cups/backend/ncp
install -c -m 755 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/cups
ln -s ../doc/%{name}-%{version} $RPM_BUILD_ROOT%{_datadir}/%{name}/doc
# Deal with users trying to access the admin tool at
# /usr/share/doc/cups-%{version}/index.html rather than the
# correct http://localhost:631/
for i in admin classes jobs printers; do
	mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/$i
	cat >$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/$i/index.html <<EOF
<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/transitional.dtd">
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="refresh" content="2; URL=http://localhost:631/$i" />
<title>CUPS $i</title>
</head>
<body bgcolor="#cccc99" text="#000000" link="#0000ff" vlink="#ff00ff">
<p>You are trying to access the CUPS admin frontend through reading the files.
The correct way to access the CUPS admin frontend is pointing your browser at
<a href="http://localhost:631/">http://localhost:631/</a>.</p>
<p>You should be automatically redirected to the correct URL in 2 seconds.
If your browser does not support redirection, please use
<a href="http://localhost:631/$i">this link</a>.</p>
</body>
</html>
EOF
done

# Ship pstoraster (bug #69573).
install -c -m 755 %{SOURCE6} $RPM_BUILD_ROOT%{_libdir}/cups/filter
install -c -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/cups

# Ship a generic postscript PPD file (#73061)
install -c -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_datadir}/cups/model

%if %use_dbus
# D-BUS configuration.
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d
install -c -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/cups.conf
%endif

# Remove unshipped files.
rm -rf $RPM_BUILD_ROOT%{_mandir}/cat? $RPM_BUILD_ROOT%{_mandir}/*/cat?

# Remove .pdf from docs, fix links
for pdf in cmp.pdf ipp.pdf sam.pdf spm.pdf ssr.pdf sum.pdf translation.pdf \
           idd.pdf overview.pdf sdd.pdf sps.pdf stp.pdf svd.pdf
do
    perl -p -i -e "s@$pdf@http://www.cups.org/$pdf@" $RPM_BUILD_ROOT%{_docdir}/cups-%{version}/documentation.html
done
find $RPM_BUILD_ROOT%{_docdir}/cups-%{version} -name *.pdf |xargs rm


%post
/sbin/chkconfig --del cupsd 2>/dev/null || true # Make sure old versions aren't there anymore
/sbin/chkconfig --add cups || true
%if %use_alternatives
/usr/sbin/alternatives --install %{_bindir}/lpr print %{_bindir}/lpr.cups 40 \
	 --slave %{_bindir}/lp print-lp %{_bindir}/lp.cups \
	 --slave %{_bindir}/lpq print-lpq %{_bindir}/lpq.cups \
	 --slave %{_bindir}/lprm print-lprm %{_bindir}/lprm.cups \
	 --slave %{_bindir}/lpstat print-lpstat %{_bindir}/lpstat.cups \
	 --slave %{_bindir}/cancel print-cancel %{_bindir}/cancel.cups \
	 --slave %{_sbindir}/lpc print-lpc %{_sbindir}/lpc.cups \
	 --slave %{_mandir}/man1/cancel.1.gz print-cancelman %{_mandir}/man1/cancel-cups.1.gz \
	 --slave %{_mandir}/man1/lp.1.gz print-lpman %{_mandir}/man1/lp-cups.1.gz \
	 --slave %{_mandir}/man8/lpc.8.gz print-lpcman %{_mandir}/man8/lpc-cups.8.gz \
	 --slave %{_mandir}/man1/lpq.1.gz print-lpqman %{_mandir}/man1/lpq-cups.1.gz \
	 --slave %{_mandir}/man1/lpr.1.gz print-lprman %{_mandir}/man1/lpr-cups.1.gz \
	 --slave %{_mandir}/man1/lprm.1.gz print-lprmman %{_mandir}/man1/lprm-cups.1.gz \
	 --slave %{_mandir}/man1/lpstat.1.gz print-lpstatman %{_mandir}/man1/lpstat-cups.1.gz \
	 --initscript cups
%endif
if [ $1 -eq 1 ]; then
  # First install.  Build ppds.dat.
  /sbin/service cups reload >/dev/null 2>&1 || :
fi
exit 0

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%preun
if [ "$1" = "0" ]; then
	/sbin/service cups stop > /dev/null 2>&1
	/sbin/chkconfig --del cups
%if %use_alternatives
        /usr/sbin/alternatives --remove print %{_bindir}/lpr.cups
%endif
fi
exit 0

%postun
if [ "$1" -ge "1" ]; then
	/sbin/service cups condrestart > /dev/null 2>&1
fi
exit 0

%triggerin -- samba-client
ln -sf ../../../bin/smbspool %{_libdir}/cups/backend/smb || :
exit 0

%triggerun -- samba-client
[ $2 = 0 ] || exit 0
rm -f %{_libdir}/cups/backend/smb

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%dir %attr(0775,root,sys) /etc/cups
%dir %attr(0711,root,sys) /etc/cups/certs
%config(noreplace) %attr(0640,root,sys) /etc/cups/classes.conf
%config(noreplace) %attr(0640,root,sys) /etc/cups/cupsd.conf
%config(noreplace) %attr(0640,root,sys) /etc/cups/printers.conf
%config(noreplace) /etc/cups/client.conf
/etc/cups/interfaces
%config(noreplace) /etc/cups/mime.types
%config(noreplace) /etc/cups/mime.convs
%dir %attr(0755,root,sys) /etc/cups/ppd
/etc/cups/pstoraster.convs
%config(noreplace) /etc/pam.d/cups
%dir %{_docdir}/cups-%{version}
%{_docdir}/cups-%{version}/images
%{_docdir}/cups-%{version}/*.css
%{_docdir}/cups-%{version}/documentation.html
%{_docdir}/cups-%{version}/??
%{_docdir}/cups-%{version}/admin
%{_docdir}/cups-%{version}/classes
%{_docdir}/cups-%{version}/jobs
%{_docdir}/cups-%{version}/printers
%doc %{_docdir}/cups-%{version}/index.html
%doc %{_docdir}/cups-%{version}/cmp.html
%doc %{_docdir}/cups-%{version}/idd.html
%doc %{_docdir}/cups-%{version}/ipp.html
%doc %{_docdir}/cups-%{version}/overview.html
%doc %{_docdir}/cups-%{version}/sam.html
%doc %{_docdir}/cups-%{version}/sdd.html
%doc %{_docdir}/cups-%{version}/spm.html
%doc %{_docdir}/cups-%{version}/sps.html
%doc %{_docdir}/cups-%{version}/ssr.html
%doc %{_docdir}/cups-%{version}/stp.html
%doc %{_docdir}/cups-%{version}/sum.html
%doc %{_docdir}/cups-%{version}/svd.html
%doc %{_docdir}/cups-%{version}/translation.html
%doc %{_docdir}/cups-%{version}/robots.txt
%config(noreplace) %{initdir}/cups
%{_bindir}/cupstestppd
%{_bindir}/cancel*
%{_bindir}/enable*
%{_bindir}/disable*
%{_bindir}/cupsenable*
%{_bindir}/cupsdisable*
%{_bindir}/lp*
%dir %{_libdir}/cups
%{_libdir}/cups/backend
%{_libdir}/cups/cgi-bin
%dir %{_libdir}/cups/daemon
%{_libdir}/cups/daemon/cups-polld
%{_libdir}/cups/filter
%{_mandir}/man?/*
%{_mandir}/*/man?/*
%{_sbindir}/*
%dir %{_datadir}/cups
%dir %{_datadir}/cups/banners
%config(noreplace) %{_datadir}/cups/banners/*
%{_datadir}/cups/charsets
%{_datadir}/cups/data
%{_datadir}/cups/doc
%{_datadir}/cups/fonts
%{_datadir}/cups/model
%{_datadir}/cups/templates
%{_datadir}/locale/*/*
%dir %attr(1770,root,sys) /var/spool/cups/tmp
%dir %attr(0710,root,sys) /var/spool/cups
%dir %attr(0755,lp,sys) /var/log/cups
%config(noreplace) %{_sysconfdir}/logrotate.d/cups
%{_datadir}/pixmaps/cupsprinter.png
%{_sysconfdir}/cron.daily/cups
%if %use_dbus
%{_sysconfdir}/dbus-1/system.d/cups.conf
%endif

%files libs
%defattr(-,root,root)
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root)
%{_bindir}/cups-config
%{_libdir}/*.so
%{_libdir}/*.a
%{_includedir}/cups

%files lpd
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/xinetd.d/cups-lpd
%dir %{_libdir}/cups
%dir %{_libdir}/cups/daemon
%{_libdir}/cups/daemon/cups-lpd

%changelog
* Thu Mar 10 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-14
- Fixed up dbus patch so that it compiles.

* Wed Mar  9 2005 John (J5) Palmieri <johnp@redhat.com>
- Fix up dbus patch 

* Mon Mar  7 2005 John (J5) Palmieri <johnp@redhat.com> 1:1.1.23-13
- Fixed up dbus patch to work with dbus 0.31

* Tue Mar  1 2005 Tomas Mraz <tmraz@redhat.com> 1:1.1.23-12
- rebuild for openssl-0.9.7e

* Tue Feb 22 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-11
- UTF-8-ify spec file (bug #149293).

* Fri Feb 18 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-10
- Fixed build with GCC 4.

* Thu Feb 10 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-9
- Back to old DBUS API since new DBUS isn't built yet.

* Mon Feb  7 2005 Tim Waugh <twaugh@redhat.com>
- Use upstream patch for STR #1068.
- Apply patch to fix remainder of CAN-2004-0888 (bug #135378).

* Wed Feb  2 2005 Tim Waugh <twaugh@redhat.com>
- Applied patch to prevent occasional cupsd crash on reload (bug #146850).

* Tue Feb  1 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-8
- New DBUS API.

* Tue Feb  1 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-7
- Applied patch to prevent file descriptor confusion (STR #1068).

* Fri Jan 28 2005 Tim Waugh <twaugh@redhat.com>
- Build does not require XFree86-devel (bug #146397).

* Thu Jan 27 2005 Tim Waugh <twaugh@redhat.com>
- Corrected directory modes so that they reflect what cupsd sets them to.

* Mon Jan 24 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-6
- Build against new dbus.

* Fri Jan 21 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-5
- Use tmpwatch to remove unused files in the spool temporary directory
  (bug #110026).

* Thu Jan 20 2005 Tim Waugh <twaugh@redhat.com>
- Use gzip's -n flag for the PPDs.

* Thu Jan 20 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-4
- Mark the initscript noreplace (bug #145629).

* Wed Jan 19 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-3
- Applied patch to fix CAN-2005-0064.

* Thu Jan  6 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-2
- Fixed patch from STR #1023.

* Tue Jan  4 2005 Tim Waugh <twaugh@redhat.com> 1:1.1.23-1
- 1.1.23.

* Mon Dec 20 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.23-0.rc1.1
- 1.1.23rc1.
- No longer need ioctl, ref-before-use, str1023 or str1024 patches.

* Fri Dec 17 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-6
- Use upstream patches for bug #143086.

* Thu Dec 16 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-5
- Fixed STR #1023 (part of bug #143086).
- Fixed STR #1024 (rest of bug #143086).

* Thu Dec  9 2004 Tim Waugh <twaugh@redhat.com>
- Not all files in the doc directory are pure documentation (bug #67337).

* Thu Dec  9 2004 Tim Waugh <twaugh@redhat.com>
- Fixed ioctl parameter size in usb backend.  Spotted by David A. Marlin.

* Fri Dec  3 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-4
- Convert de and fr .tmpl files into UTF-8 (bug #136177).

* Thu Dec  2 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-3
- Fix ref-before-use bug in debug output (bug #141585).

* Mon Nov 29 2004 Tim Waugh <twaugh@redhat.com>
- Copied "ext" patch over from xpdf RPM package.

* Mon Nov 22 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-2
- Fixed cups-lpd file mode (bug #137325).
- Convert all man pages to UTF-8 (bug #107118).  Patch from Miloslav Trmac.

* Mon Nov  8 2004 Tim Waugh <twaugh@redhat.com>
- New lpd subpackage, from patch by Matthew Galgoci (bug #137325).

* Tue Nov  2 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-1
- 1.1.22.
- No longer need ippfail, overread or str970 patches.

* Tue Oct 26 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc2.1
- Make cancel-cups(1) man page point to lp-cups(1) not lp(1) (bug #136973).
- Use upstream patch for STR #953.
- 1.1.22rc2.

* Wed Oct 20 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc1.7
- Prevent filters generating incorrect PS in locales where "," is the
  decimal separator (bug #136102).  Patch from STR #970.

* Thu Oct 14 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc1.5
- Fixed another typo in last patch!

* Thu Oct 14 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc1.4
- Fixed typo in last patch.

* Thu Oct 14 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc1.3
- Another attempt at fixing bug #135502.

* Wed Oct 13 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc1.2
- Fail better when receiving corrupt IPP responses (bug #135502).

* Mon Oct 11 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.22-0.rc1.1
- 1.1.22rc1.

* Tue Oct  5 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-7
- Set LogFilePerm 0600 in default config file.

* Tue Oct  5 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-6
- Apply patch to fix CAN-2004-0923 (bug #134601).

* Mon Oct  4 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-5
- Fixed reload logic (bug #134080).

* Wed Sep 29 2004 Warren Togami <wtogami@redhat.com> 1:1.1.21-4
- Remove .pdf from docs, fix links

* Fri Sep 24 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-3
- Write a pid file (bug #132987).

* Thu Sep 23 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-2
- 1.1.21.

* Thu Sep  9 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc2.2
- Updated DBUS patch (from Colin Walters).

* Tue Aug 24 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc2.1
- 1.1.21rc2.
- No longer need state, reload-timeout or str743 patches.
- httpnBase64 patch no longer applies; alternate method implemented
  upstream.
- Fix single byte overread in usersys.c (spotted by Colin Walters).

* Wed Aug 18 2004 Tim Waugh <twaugh@redhat.com>
- Applied httpnEncode64 patch from Colin Walters.

* Sun Aug 15 2004 Tim Waugh <twaugh@redhat.com>
- Session printing patch (Colin Walters).  Disabled for now.

* Sun Aug 15 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.9
- Shorter reload timeout (Colin Walters).
- Updated DBUS patch from Colin Walters.

* Fri Aug 13 2004 Tim Waugh <twaugh@redhat.com>
- Updated IPP backend IPP_PORT patch from Colin Walters.

* Fri Aug 13 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.8
- Preserve DBUS_SESSION_BUS_ADDRESS in environment (Colin Walters).
- Fixed enabledisable patch.

* Fri Aug 13 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.7
- Bumped DBUS version to 0.22.

* Fri Aug  6 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.6
- Patch from Colin Walters to prevent IPP backend using non-standard
  IPP port.

* Sun Aug  1 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.5
- Really bumped DBUS version.

* Fri Jul 30 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.4
- Bumped DBUS version.

* Fri Jul 16 2004 Tim Waugh <twaugh@redhat.com>
- Added version to LPRng obsoletes: tag (bug #128024).

* Thu Jul  8 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.3
- Updated DBUS patch.

* Tue Jun 29 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.2
- Apply patch from STR #743 (bug #114999).

* Fri Jun 25 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-1.rc1.1
- Fix permissions on logrotate script (bug #126426).

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jun  4 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-0.rc1.2
- Build for dbus-0.21.
- Fix SetPrinterState().

* Thu Jun  3 2004 Tim Waugh <twaugh@redhat.com>
- Use configure's --with-optim parameter instead of setting OPTIM at
  make time (bug #125228).

* Thu Jun  3 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.21-0.rc1.1
- 1.1.21rc1.
- No longer need str716, str718, authtype or encryption patches.

* Wed Jun  2 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-15
- Build on ppc and ppc64 again.

* Wed Jun  2 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-14
- ExcludeArch ppc, ppc64.
- More D-BUS changes.

* Tue Jun  1 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-13
- Enable optimizations on ia64 again.

* Thu May 27 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-12
- D-BUS changes.

* Wed May 26 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-11
- Build requires make >= 3.80 (bug #124472).

* Wed May 26 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-10
- Finish fix for cupsenable/cupsdisable (bug #102490).
- Fix MaxLogSize setting (bug #123003).

* Tue May 25 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-9
- Apply patches from CVS (authtype) to fix STR #434, STR #611, and as a
  result STR #719.  This fixes several problems including those noted in
  bug #114999.

* Mon May 24 2004 Tim Waugh <twaugh@redhat.com>
- Use upstream patch for exit code fix for bug #110135 [STR 718].

* Wed May 19 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-8
- If cupsd fails to start, make it exit with an appropriate code so that
  initlog notifies the user (bug #110135).

* Thu May 13 2004 Tim Waugh <twaugh@redhat.com>
- Fix cups/util.c:get_num_sdests() to use encryption when it is necessary
  or requested (bug #118982).
- Use upstream patch for the HTTP/1.1 Continue bug (from STR716).

* Tue May 11 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-7
- Fix non-conformance with HTTP/1.1, which caused failures when printing
  to a Xerox Phaser 8200 via IPP (bug #122352).
- Make lppasswd(1) PIE.
- Rotate logs within cupsd (instead of relying on logrotate) if we start
  to approach the filesystem file size limit (bug #123003).

* Tue Apr  6 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-6
- Fix pie patch (bug #120078).

* Fri Apr  2 2004 Tim Waugh <twaugh@redhat.com>
- Fix rcp patch for new system-config-printer name.

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb  6 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-4
- Tracked D-BUS API changes.
- Updated D-BUS configuration file.
- Symlinks to avoid conflicting with bash builtins (bug #102490).

* Thu Feb  5 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-3
- Improved PIE patch.
- Fixed compilation with GCC 3.4.

* Thu Jan 29 2004 Tim Waugh <twaugh@redhat.com>
- Don't ship cupsconfig now that nothing uses it.

* Wed Jan  7 2004 Tim Waugh <twaugh@redhat.com> 1:1.1.20-2
- Try harder to find a translated page for the web interface (bug #107619).
- Added build_as_pie conditional to spec file to facilitate debugging.

* Mon Dec  1 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.20-1
- 1.1.20.
- No longer need idefense, str226 patches.
- Updated sanity patch.
- The devel sub-package requires openssl-devel (bug #110772).

* Wed Nov 26 2003 Thomas Woerner <twoerner@redhat.com> 1:1.1.19-16
- removed -Wl,-rpath from cups-sharedlibs.m4 (replaced old no_rpath patch)

* Tue Nov 25 2003 Thomas Woerner <twoerner@redhat.com> 1:1.1.19-15
- no rpath in cups-config anymore

* Thu Nov 20 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-14
- Enable PIE for cupsd.

* Fri Nov 14 2003 Tim Waugh <twaugh@redhat.com>
- Don't ignore the file descriptor when ShutdownClient is called: it
  might get closed before we next try to read it (bug #107787).

* Tue Oct 14 2003 Tim Waugh <twaugh@redhat.com>
- Removed busy-loop patch; 1.1.19 has its own fix for this.

* Thu Oct  2 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-13
- Apply patch from STR 226 to make CUPS reload better behaved (bug #101507).

* Wed Sep 10 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-12
- Prevent a libcups busy loop (bug #97958).

* Thu Aug 14 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-11
- Another attempt to fix bug #100984.

* Wed Aug 13 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-10
- Pass correct attributes-natural-language through even in the absence
  of translations for that language (bug #100984).
- Show compilation command lines.

* Wed Jul 30 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-9
- Prevent lpstat displaying garbage.

* Mon Jul 21 2003 Tim Waugh <twaugh@redhat.com>
- Mark mime.convs and mime.types as config files (bug #99461).

* Mon Jun 23 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-8
- Start cupsd before nfs server processes (bug #97767).

* Tue Jun 17 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-7
- Add some %if %use_dbus / %endif's to make it compile without dbus
  (bug #97397).  Patch from Jos Vos.

* Mon Jun 16 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-6
- Don't busy loop in the client if the IPP port is in use by another
  app (bug #97468).

* Tue Jun 10 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-5
- Mark pam.d/cups as config file not to be replaced (bug #92236).

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun  3 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-3
- Provide a version for LPRng (bug #92145).

* Thu May 29 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-2
- Obsolete LPRng now.

* Tue May 27 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-1
- 1.1.19.  No longer need optparse patch.

* Sat May 17 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-0.rc5.4
- Ship configuration file for D-BUS.

* Fri May 16 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-0.rc5.3
- Rebuild for dbus-0.11 API changes.
- Fix ownership in file manifest (bug #90840).

* Wed May 14 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-0.rc5.2
- Fix option parsing in lpq (bug #90823).

* Tue May 13 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-0.rc5.1
- 1.1.19rc5.

* Thu May  8 2003 Tim Waugh <twaugh@redhat.com> 1:1.1.19-0.rc4.1
- 1.1.19rc4.  Ported initscript, idefense, ppdsdat, dbus patches.
- No longer need error, sigchld patches.
- Ship cupstestppd.

* Thu Apr 24 2003 Tim Waugh <twaugh@redhat.com>
- Mark banners as config files (bug #89069).

* Sat Apr 12 2003 Havoc Pennington <hp@redhat.com> 1:1.1.18-4
- adjust dbus patch - dbus_bus_get() sends the hello for you, 
  and there were a couple of memleaks
- buildprereq dbus 0.9
- rebuild for new dbus
- hope it works, I'm ssh'd in with no way to test. ;-)

* Thu Apr 10 2003 Tim Waugh <twaugh@redhat.com> 1.1.18-3
- Get on D-BUS.

* Fri Mar 28 2003 Tim Waugh <twaugh@redhat.com> 1.1.18-2
- Fix translation in the init script (bug #87551).

* Wed Mar 26 2003 Tim Waugh <twaugh@redhat.com> 1.1.18-1.1
- Turn off optimization on ia64 until bug #87383 is fixed.

* Wed Mar 26 2003 Tim Waugh <twaugh@redhat.com> 1.1.18-1
- 1.1.18.
- No longer need uninit patch.
- Some parts of the iDefense and pdftops patches seem to have been
  picked up, but not others.

* Wed Feb 12 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-13
- Don't set SIGCHLD to SIG_IGN when using wait4 (via pclose) (bug #84101).

* Tue Feb  4 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-12
- Fix cups-lpd (bug #83452).

* Fri Jan 31 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-11
- Build ppds.dat on first install.

* Fri Jan 24 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-10
- Add support for rebuilding ppds.dat without running the scheduler
  proper (for bug #82500).

* Wed Jan 22 2003 Tim Powers <timp@redhat.com> 1.1.17-9
- rebuilt

* Wed Jan 22 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-8
- Warn against editing queues managed by redhat-config-printer
  (bug #82267).

* Wed Jan 22 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-7
- Fix up error reporting in lpd backend.

* Thu Jan  9 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-6
- Add epoch to internal requirements.
- Make 'condrestart' return success exit code when daemon isn't running.

* Tue Jan  7 2003 Nalin Dahyabhai <nalin@redhat.com> 1.1.17-5
- Use pkg-config information to find SSL libraries.

* Thu Dec 19 2002 Tim Waugh <twaugh@redhat.com> 1.1.17-4
- Security fixes.
- Make 'service cups reload' update the configuration first (bug #79953).

* Tue Dec 10 2002 Tim Waugh <twaugh@redhat.com> 1.1.17-3
- Fix cupsd startup hang (bug #79346).

* Mon Dec  9 2002 Tim Waugh <twaugh@redhat.com> 1.1.17-2
- Fix parallel backend behaviour when cancelling jobs.

* Mon Dec  9 2002 Tim Waugh <twaugh@redhat.com> 1.1.17-1
- 1.1.17.
- No longer need libdir patch.
- Fix logrotate script (bug #76791).

* Wed Nov 20 2002 Tim Waugh <twaugh@redhat.com>
- Build requires XFree86-devel (bug #78362).

* Wed Nov 20 2002 Tim Waugh <twaugh@redhat.com>
- 1.1.16.
- Updated system-auth patch.
- Add ncp backend script.

* Wed Nov 13 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-15
- Set alternatives priority to 40.

* Mon Nov 11 2002 Nalin Dahyabhai <nalin@redhat.com> 1.1.15-14
- Buildrequire pam-devel.
- Patch default PAM config file to remove directory names from module paths,
  allowing the configuration files to work equally well on multilib systems.
- Patch default PAM config file to use system-auth, require the file at build-
  time because that's what data/Makefile checks for.

* Fri Nov  8 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-13
- Use logrotate for log rotation (bug #76791).
- No longer need cups.desktop, since redhat-config-printer handles it.

* Thu Oct 17 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-12
- Revert to libdir for CUPS_SERVERBIN.

* Thu Oct 17 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-11
- Use %%configure for multilib correctness.
- Use libexec instead of lib for CUPS_SERVERBIN.
- Ship translated man pages.
- Remove unshipped files.
- Fix file list permissions (bug #59021, bug #74738).
- Fix messy initscript output (bug #65857).
- Add 'reload' to initscript (bug #76114).

* Fri Aug 30 2002 Bernhard Rosenkraenzer <bero@redhat.de> 1.1.15-10
- Add generic postscript PPD file (#73061)

* Mon Aug 19 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-9
- Fix prefix in pstoraster (bug #69573).

* Mon Aug 19 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-8
- Disable cups-lpd by default (bug #71712).
- No need for fread patch now that glibc is fixed.

* Thu Aug 15 2002 Tim Waugh <twaugh@redhat.com> 1.1.15-7
- Really add cups-lpd xinetd file (bug #63919).
- Ship pstoraster (bug #69573).
- Prevent fread from trying to read from beyond EOF (fixes a segfault
  with new glibc).

* Sat Aug 10 2002 Elliot Lee <sopwith@redhat.com> 1.1.15-6
- rebuilt with gcc-3.2 (we hope)

* Mon Aug  5 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.15-5
- Add cups-lpd xinetd file (#63919)

* Tue Jul 23 2002 Florian La Roche <Florian.LaRoche@redhat.de> 1.1.15-4
- add a "exit 0" to postun script

* Tue Jul  2 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.15-3
- Add a symlink /usr/share/cups/doc -> /usr/share/doc/cups-devel-1.1.15
  because some applications expect to find the cups docs in
  /usr/share/cups/doc

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Jun 21 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.15-1
- 1.1.15-1
- Fix up smb printing trigger (samba-client, not samba-clients)
- Start cupsd earlier, apparently it needs to be running before samba
  starts up for smb printing to work.

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May  7 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-17
- Rebuild in current environment
- [-16 never existed because of build system breakage]

* Wed Apr 17 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-15
- Fix bug #63387

* Mon Apr 15 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-14
- Fix dangling symlink created by samba-clients trigger

* Wed Apr 10 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-13
- Add desktop file and icon for CUPS configuration

* Wed Apr  3 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-12
- Support SMB printing (#62407)
- Add HTML redirections to doc files to work around users mistaking
  /usr/share/doc/cups-1.1.14 for the web frontend (#62405)

* Tue Apr  2 2002 Bill Nottingham <notting@redhat.com> 1.1.14-11
- fix subsys in initscript (#59206)
- don't strip binaries

* Mon Mar 11 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-10
- Make initscript use killproc instead of killall

* Fri Mar  8 2002 Bill Nottingham <notting@redhat.com> 1.1.14-9
- use alternatives --initscript support

* Mon Mar  4 2002 Bill Nottingham <notting@redhat.com> 1.1.14-8
- use the right path for the lpc man page, duh

* Thu Feb 28 2002 Bill Nottingham <notting@redhat.com> 1.1.14-7
- lpc man page is alternative too
- run ldconfig in -libs %post/%postun, not main
- remove alternatives in %preun

* Wed Feb 27 2002 Bill Nottingham <notting@redhat.com> 1.1.14-6
- don't source /etc/sysconfig/network in cups.init, we don't use any
  values from it

* Tue Feb 26 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-4
- Fix bugs #60220 and #60352

* Thu Feb 21 2002 Tim Powers <timp@redhat.com>
- rebuild against correct version of openssl (0.9.6b)

* Wed Feb 20 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-2
- Add all man pages to alternatives (#59943)
- Update to real 1.1.14

* Tue Feb 12 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.14-1
- Update to almost-1.1.14

* Mon Feb 11 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.13-5
- Move cups-config to cups-devel subpackage
- Make alternatives usage a %%define to simplify builds for earlier
  releases
- Explicitly provide things we're supplying through alternatives
  to shut up kdeutils dependencies

* Tue Feb  5 2002 Tim Powers <timp@redhat.com>
- shut the alternatives stuff up for good

* Fri Feb  1 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.13-3
- Fix alternatives stuff
- Don't display error messages in %%post

* Wed Jan 30 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.13-2
- alternatives stuff

* Tue Jan 29 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.13-1
- 1.1.13
- Add patch for koi8-{r,u} and iso8859-8 encodings (#59018)
- Rename init scripts so we can safely "killall cupsd" from there

* Sat Jan 26 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.12-1
- Initial (conflicting, since alternatives isn't there yet) packaging for
  Red Hat Linux

* Sat Jan 19 2002 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.1.12

* Mon Nov  5 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.10-3
- Compress PPD files
- Fix build with gcc 3.1
- Fix init script

* Tue Sep  4 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.10-2
- Fix URL
- Generate printcap
- s/Copyright/License/g

* Tue Sep  4 2001 Than Ngo <than@redhat.com> 1.1.10-1
- update to 1.1.10-1 for ExtraBinge 7.2

* Tue May 29 2001 Michael Stefaniuc <mstefani@redhat.com>
- update to 1.1.8
- changed cupsd.conf to generate /etc/printcap

* Tue May 15 2001 Than Ngo <than@redhat.com>
- update to 1.1.7, bugfixes

* Thu Dec 14 2000 Than Ngo <than@redhat.com>
- fixed package dependency with lpr and LPRng

* Wed Oct 25 2000 Than Ngo <than@redhat.com>
- remove man/cat

* Tue Oct 24 2000 Than Ngo <than@redhat.com>
- don't start cupsd service in level 0, fixed

* Thu Oct 19 2000 Than Ngo <than@redhat.com>
- update to 1.1.4
- fix CUPS_DOCROOT (Bug #18717)

* Fri Aug 11 2000 Than Ngo <than@redhat.de>
- update to 1.1.2 (Bugfix release)

* Fri Aug 4 2000 Than Ngo <than@redhat.de>
- fix, cupsd read config file under /etc/cups (Bug #15432)
- add missing cups filters

* Wed Aug 2 2000 Tim Powers <timp@redhat.com>
- rebuilt against libpng-1.0.8

* Tue Aug 01 2000 Than Ngo <than@redhat.de>
- fix permission, add missing ldconfig in %post and %postun (Bug #14963)

* Sat Jul 29 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.1.1 (this has some major bugfixes)
- Fix a typo in initscript (it's $?, not ?$)
- Fix /usr/etc vs. /etc trouble, don't insist on /usr/var (YUCK!)
- Create the spool dir

* Fri Jul 28 2000 Than Ngo <than@redhat.de>
- fix unclean code for building against gcc-2.96
- add missing restart function in startup script

* Fri Jul 28 2000 Tim Powers <timp@redhat.com>
- fixed initscript so that conrestart doesn't return 1 if the test fails

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Wed Jul 19 2000 Than Ngo <than@redhat.de>
- using service to fire them up
- fix Prereq section

* Mon Jul 17 2000 Tim Powers <timp@redhat.com>
- added defattr to the devel package

* Sun Jul 16 2000 Than Ngo <than@redhat.de>
- add cups config files

* Sat Jul 15 2000 Than Ngo <than@redhat.de>
- update to 1.1 release
- move back to /etc/rc.d/init.d
- fix cupsd.init to work with /etc/init.d and /etc/rc.d/init.d
- split cups

* Wed Jul 12 2000 Than Ngo <than@redhat.de>
- rebuilt

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- fixed broken PreReq to now require /etc/init.d

* Tue Jun 27 2000 Tim Powers <timp@redhat.com>
- PreReq initscripts >= 5.20

* Mon Jun 26 2000 Tim Powers <timp@redhat.com>
- started changelog 
- fixed init.d script location
- changed script in init.d quite a bit and made more like the rest of our
  startup scripts 
