%define name pdq
%define version 2.2.1
%define release %mkrel 14

Summary:   Print, don't Queue! - Daemonless printing system
Name:      %{name}
Version:   %{version}
Release:   %{release}
Group:     System/Servers
URL:       http://pdq.sourceforge.net/
Patch0:    %{name}-%{version}-Makefile.in-0.patch.bz2
Patch1:    %{name}-%{version}-Makefile.in-1.patch.bz2
Patch2:	   %{name}-%{version}-open-with-default-open-umask.patch
Source1:   pdqpanicbutton.bz2
Source2:   killpdq.bz2
License:   GPL
Source:    %{name}-%{version}.tar.bz2
Requires:  file
BuildRequires:	gtk+-devel
#Provides:  lpddaemon
BuildRoot: %{_tmppath}/%{name}-buildroot

%description 
A complete replacement for classical printing systems (spoolers). PDQ
does not need a daemon and so there are no problems with crashed
daemons, blocked ports, attacks of open ports, but PDQ cannot receive
jobs from remote machines.

PDQ comes with a graphical interface and LPD backend filters (to print
on a remote LPD printer or to serve as frontend for a local LPD
system).

This system is a good choice for non-networked (only dial-up to the
internet) machines, because it does not contain all the network stuff
of other spoolers which causes difficulties for users without network.

%prep
rm -rf $RPM_BUILD_ROOT

%setup

%patch0
%patch1
%patch2 -p1

%build

%configure --enable-pdqlibdir=%{_libdir}/pdq --enable-printrc=%{_sysconfdir}/pdq/printrc --prefix=%{_prefix}

%make

%install
#mkdir -p ${RPM_BUILD_ROOT}/etc/pdq/drivers/{generic,ghostscript,misc,postscript}
#mkdir -p ${RPM_BUILD_ROOT}/etc/pdq/interfaces
mkdir -p ${RPM_BUILD_ROOT}/etc/pdq
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/{man1,man5}

make install prefix=${RPM_BUILD_ROOT}%{_prefix} \
	bindir=${RPM_BUILD_ROOT}%{_bindir} \
	xpdqbindir=${RPM_BUILD_ROOT}%{_bindir} \
	libdir=${RPM_BUILD_ROOT}%{_libdir} \
	infodir=${RPM_BUILD_ROOT}%{_infodir} \
	mandir=$RPM_BUILD_ROOT%{_mandir} \
	pdqlibdir=${RPM_BUILD_ROOT}%{_libdir}/pdq \
	printrc_file=${RPM_BUILD_ROOT}%{_sysconfdir}/pdq/printrc

mv ${RPM_BUILD_ROOT}%{_libdir}/pdq/printrc.example \
   ${RPM_BUILD_ROOT}%{_sysconfdir}/pdq/printrc

# Install the stuff for the panic button

install -d ${RPM_BUILD_ROOT}%{_sbindir}
bzcat %{SOURCE1} > ${RPM_BUILD_ROOT}%{_sbindir}/pdqpanicbutton
bzcat %{SOURCE2} > ${RPM_BUILD_ROOT}%{_bindir}/killpdq
chmod a+rx ${RPM_BUILD_ROOT}%{_sbindir}/pdqpanicbutton
chmod a+rx ${RPM_BUILD_ROOT}%{_bindir}/killpdq

# Use update-alternatives to make printing with PDQ also possible with
# the "lpr" command

( cd $RPM_BUILD_ROOT%{_bindir}
  ln -s pdq lpr-pdq
)
( cd $RPM_BUILD_ROOT/%{_mandir}/man1
  ln -s pdq.1 lpr-pdq.1
)

%clean
rm -rf $RPM_BUILD_ROOT

%post

# Set up update-alternatives entry
%{_sbindir}/update-alternatives --install %{_bindir}/lpr lpr %{_bindir}/lpr-pdq 6 --slave %{_mandir}/man1/lpr.1.bz2 lpr.1.bz2 %{_mandir}/man1/lpr-pdq.1.bz2

%preun

if [ "$1" = 0 ]; then
  # Remove update-alternatives entry
  %{_sbindir}/update-alternatives --remove lpr /usr/bin/lpr-pdq
  # Remove panic-buttons
  %{_sbindir}/pdqpanicbutton --remove
fi

%files
%defattr(-,root,root,755)
%doc ./doc/*.txt ./doc/PROPOSED_CHANGES BUGS
%doc CHANGELOG INSTALL LICENSE README

%defattr(644,root,root,755)
#dir %{_sysconfdir}/pdq
%config(noreplace) %{_sysconfdir}/pdq/printrc
%{_libdir}/pdq/drivers
%{_libdir}/pdq/interfaces
  
%attr(4755,root,root) %{_bindir}/lpd_*
%attr(755,root,root) %{_bindir}/pdq
%attr(755,root,root) %{_bindir}/xpdq
%{_bindir}/lpr-pdq
%attr(755,root,root) %{_bindir}/killpdq
%attr(755,root,root) %{_sbindir}/pdqpanicbutton

%{_mandir}/man1/lpd_*
%{_mandir}/man1/lpr-pdq*
%{_mandir}/man1/*pdq*
%{_mandir}/man5/printrc.5*
