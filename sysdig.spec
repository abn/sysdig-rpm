%global _hardened_build 1

Name:               sysdig
Version:            0.6.0
Release:            1
Summary:            Linux system exploration and troubleshooting tool with first class support for containers
License:            GPLv2+
Group:              Applications/Engineering
URL:                http://www.sysdig.org/
Source0:            https://github.com/draios/sysdig/archive/%{version}.tar.gz

# This patch is required till a new version of jsoncpp with nullRef is available in distro
# https://github.com/draios/sysdig/issues/377
Patch0:             0001-Revert-Json-Value-nullRef-usage.patch

BuildRequires:      gcc-c++
BuildRequires:      make
BuildRequires:      cmake
BuildRequires:      kernel
BuildRequires:      kernel-headers
BuildRequires:      kernel-devel
BuildRequires:      luajit-devel
BuildRequires:      jsoncpp-devel
BuildRequires:      ncurses-devel
BuildRequires:      libcurl-devel
BuildRequires:      zlib-devel
BuildRequires:      openssl-devel
BuildRequires:      systemd

Requires:           luajit
Requires:           zlib
Requires:           ncurses
Requires:           base64
Requires:           openssl
Requires:           libcurl

Requires(post):     systemd
Requires(post):     dkms
Requires(post):     kernel-devel
Requires(preun):    systemd
Requires(preun):    dkms
Requires(postun):   systemd

%description

%prep
%autosetup -p1

%build
rm -f CMakeCache.txt
mkdir build
cd build

export CFLAGS="%{optflags} -Wno-return-type"
cmake \
    -DSYSDIG_VERSION=%{version} \
    -DDIR_ETC=/etc \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DUSE_BUNDLED_DEPS=OFF \
    -DUSE_BUNDLED_B64=YES ..
make %{?_smp_mflags}

%install
cd build
%make_install
make install_driver

%post
%systemd_post %{name}.service

dkms add -m sysdig -v %{version} --rpm_safe_upgrade
if [ `uname -r | grep -c "BOOT"` -eq 0 ] && [ -e /lib/modules/`uname -r`/build/include ]; then
	dkms build -m sysdig -v %{version}
	dkms install --force -m sysdig -v %{version}
elif [ `uname -r | grep -c "BOOT"` -gt 0 ]; then
	echo -e ""
	echo -e "Module build for the currently running kernel was skipped since you"
	echo -e "are running a BOOT variant of the kernel."
else
	echo -e ""
	echo -e "Module build for the currently running kernel was skipped since the"
	echo -e "kernel source for this kernel does not seem to be installed."
fi

%preun
%systemd_preun %{name}.service
dkms remove -m sysdig -v %{version} --all --rpm_safe_upgrade

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root)
%doc COPYING README.md
#
%{_bindir}/csysdig
%{_bindir}/sysdig
%{_bindir}/sysdig-probe-loader
#
%{_prefix}/lib/debug%{_bindir}/csysdig.debug
%{_prefix}/lib/debug%{_bindir}/sysdig.debug
#
%{_sysconfdir}/bash_completion.d/sysdig
#
%{_mandir}/man8/*
#
%{_datarootdir}/sysdig/chisels/COPYING
%{_datarootdir}/sysdig/chisels/*.lua
%{_datarootdir}/zsh/site-functions/_sysdig
%{_datarootdir}/zsh/vendor-completions/_sysdig
#
%{_usrsrc}/debug/%{name}-%{version}/build/b64-prefix
%{_usrsrc}/debug/%{name}-%{version}/build/userspace/libscap
%{_usrsrc}/debug/%{name}-%{version}/build/userspace/libsinsp
%{_usrsrc}/debug/%{name}-%{version}/build/userspace/sysdig
%{_usrsrc}/debug/%{name}-%{version}/driver/*
%{_usrsrc}/debug/%{name}-%{version}/userspace/libscap/*
%{_usrsrc}/debug/%{name}-%{version}/userspace/libsinsp/*
%{_usrsrc}/debug/%{name}-%{version}/userspace/sysdig/*
%{_usrsrc}/%{name}-%{version}/*

%changelog
