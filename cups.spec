%define initdir /etc/rc.d/init.d
%define patchlevel %{nil}
%define use_alternatives 1

Summary: Common Unix Printing System
Name: cups
Version: 1.1.17
Release: 0.7
License: GPL
Group: System Environment/Daemons
%if "%{patchlevel}" != ""
Source: ftp://ftp.easysw.com/pub/cups/cups-%{version}-%{patchlevel}-source.tar.bz2
%else
Source: ftp://ftp.easysw.com/pub/cups/cups-%{version}-source.tar.bz2
%endif
Source1: cups.init
Source2: cupsprinter.png
Source3: cups.desktop
Source4: cupsconfig
Source5: cups-lpd
Source6: pstoraster
Source7: pstoraster.convs
Source8: postscript.ppd.gz
Patch: cups-1.1.15-initscript.patch
Patch1: cups-1.1.14-doclink.patch
Patch2: cups-1.1.17-uninit.patch
Patch3: cups-idefense-v2.patch
Patch4: cups-1.1.17-pdftops.patch
Patch5: cups-1.1.18-str75.patchv2
Epoch: 1
Url: http://www.cups.org/
BuildRoot: %{_tmppath}/%{name}-root
PreReq: /sbin/chkconfig /sbin/service
Requires: %{name}-libs = %{version} htmlview xinetd
%if %use_alternatives
Provides: /usr/bin/lpq /usr/bin/lpr /usr/bin/lp /usr/bin/cancel /usr/bin/lprm /usr/bin/lpstat
Prereq: /usr/sbin/alternatives
%else
Obsoletes: lpd lpr LPRng printconf printconf-gui printconf-tui printtool
Provides: lpd lpr LPRng
%endif

%package devel
Summary: Common Unix Printing System - development environment
Group: Development/Libraries
Requires: %{name}-libs = %{version}

%package libs
Summary: Common Unix Printing System - libraries
Group: System Environment/Libraries

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

%prep
%setup -q
%patch -p1 -b .noinit
%patch1 -p1 -b .doclink
%patch2 -p1 -b .uninit
%patch3 -p0 -b .security
%patch4 -p1 -b .pdftops
%patch5 -p1 -b .str75
perl -pi -e 's,^#(Printcap\s+/etc/printcap),$1,' conf/cupsd.conf.in
autoconf

%build
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" ./configure --sysconfdir=/etc \
            --with-docdir=%{_docdir}/cups-%{version} \
            --mandir=%{_mandir}
perl -pi -e "s,^DSO	=.*,DSO=gcc -fpic," Makedefs

# If we got this far, all prerequisite libraries must be here.
make OPTIM="$RPM_OPT_FLAGS -fpic"

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{initdir}

make BUILDROOT=$RPM_BUILD_ROOT install 

install -m 755 $RPM_SOURCE_DIR/cups.init $RPM_BUILD_ROOT%{initdir}/cups

find $RPM_BUILD_ROOT/usr/share/cups/model -name "*.ppd" |xargs gzip -9f

%if %use_alternatives
cd $RPM_BUILD_ROOT%{_bindir}
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i $i.cups
done
cd $RPM_BUILD_ROOT%{_sbindir}
mv lpc lpc.cups
cd $RPM_BUILD_ROOT%{_mandir}/man1
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i.1 $i-cups.1
done
cd $RPM_BUILD_ROOT%{_mandir}/man8
mv lpc.8 lpc-cups.8
%endif

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps $RPM_BUILD_ROOT%{_sysconfdir}/X11/sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/System $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d
install -c -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -c -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/X11/sysconfig
install -c -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/System
install -c -m 755 %{SOURCE4} $RPM_BUILD_ROOT%{_bindir}
install -c -m 755 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d
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

# Remove unshipped files.
rm -rf $RPM_BUILD_ROOT%{_mandir}/cat? $RPM_BUILD_ROOT%{_mandir}/*/cat? \
	$RPM_BUILD_ROOT%{_mandir}/fr
                                                                                
# Ship pstoraster (bug #69573).
install -c -m 755 %{SOURCE6} $RPM_BUILD_ROOT%{_libdir}/cups/filter
install -c -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/cups

# Ship a generic postscript PPD file (#73061)
install -c -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_datadir}/cups/model

%post
/sbin/chkconfig --del cupsd 2>/dev/null || true # Make sure old versions aren't there anymore
/sbin/chkconfig --add cups || true
%if %use_alternatives
/usr/sbin/alternatives --install %{_bindir}/lpr print %{_bindir}/lpr.cups 20 \
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
%dir /etc/cups
/etc/cups/certs
%config /etc/cups/*.conf
/etc/cups/interfaces
/etc/cups/mime.types
/etc/cups/mime.convs
/etc/cups/ppd
/etc/cups/pstoraster.convs
/etc/pam.d/cups
%doc %{_docdir}/cups-%{version}
%config %{initdir}/cups
%{_bindir}/cupsconfig
%{_bindir}/cancel*
%{_bindir}/enable*
%{_bindir}/disable*
%{_bindir}/lp*
%{_libdir}/cups
%{_mandir}/man?/*
%{_sbindir}/*
%{_datadir}/cups
%{_datadir}/locale/*/*
%dir %attr(1700,lp,root) /var/spool/cups/tmp
%dir %attr(0700,lp,root) /var/spool/cups
%dir %attr(0755,lp,root) /var/log/cups
%{_sysconfdir}/X11/sysconfig/cups.desktop
%{_sysconfdir}/X11/applnk/System/cups.desktop
%config(noreplace) %{_sysconfdir}/xinetd.d/cups-lpd
%{_datadir}/pixmaps/cupsprinter.png

%files libs
%defattr(-,root,root)
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root)
%{_bindir}/cups-config
%{_libdir}/*.so
%{_libdir}/*.a
%{_includedir}/cups

%changelog
* Fri May 15 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-0.7
- Rebuild for debug stripping.

* Thu May 15 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-0.5
- Fix typo.

* Tue May 13 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-0.4
- Update HTTP blocking fix to cups-1.1.18-str75.patchv2.

* Mon May 12 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-0.3
- Fix HTTP blocking issue with scheduler: http://www.cups.org/str.php?L75.

* Wed Jan  8 2003 Tim Waugh <twaugh@redhat.com> 1.1.17-0.2
- Fix 'condrestart' behaviour in init script.

* Fri Dec 13 2002 Tim Waugh <twaugh@redhat.com> 1.1.17-0.1
- 1.1.17.
- Fix cupsd startup hang (bug #79346).
- Don't install files not shipped.
- Security fixes.

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
