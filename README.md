# CUPS
VCS CUPS repository for :
* https://copr.fedorainfracloud.org/coprs/dkosovic/printing-el8/
* https://copr.fedorainfracloud.org/coprs/dkosovic/printing-el9/

This repository started off as a git clone of the rawhide branch of cups
from Fedora Package Sources:
* https://src.fedoraproject.org/rpms/cups/tree/rawhide

This repository contains modifications to send log output to
`/var/log/cups/error_logi` rather than system journal, fixes for Konica
Minolta printers and other local customizations. It has only been tested as
a CUPS server, not a client.

### Building on Fedora Copr

Select **Custom** for the source type.

Copy and paste the following script into the custom script text box:

```sh
#! /bin/sh

set -x # verbose output
set -e # fail the whole script if some command fails
                 
git clone https://github.com/eait-cups-printing/cups.git
mv cups/* .
rm -rf cups plans ci.fmf gating.yaml leapp_upgrades

version=`grep Version: cups.spec | awk '{ print $2 }'`
source=`grep Source0: cups.spec | awk '{print $2}' | sed "s/%{VERSION}/$version/g"`

curl -OL $source
```

Copy and paste the following into the build dependencies field:
```
git
automake
gcc
krb5-devel
libacl-devel
make
openldap-devel
pam-devel
pkgconf-pkg-config
pkgconfig(avahi-client)
pkgconfig(dbus-1)
pkgconfig(gnutls)
pkgconfig(libsystemd)
pkgconfig(libusb-1.0)
python3-cups
systemd
systemd-rpm-macros
zlib-devel
libselinux-devel
audit-libs-devel
```

