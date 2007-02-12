#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	smp		# don't build SMP module
#
%define         _orig_name      ip_wccp

%define	_rel	1
Summary:	Kernel module for WCCP protocol
Summary(pl.UTF-8):   Moduł kernela do obsługi protokołu WCCP
Name:		kernel-net-%{_orig_name}
Version:	1.6.2
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.squid-cache.org/WCCP-support/Linux/%{_orig_name}-%{version}.tar.gz
# Source0-md5:	5c198bb4aa26cab8c7576664c0f257b9
BuildRequires:	%{kgcc_package}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.0}
BuildRequires:	rpmbuild(macros) >= 1.118
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WCCP protocol support for Linux.

%description -l pl.UTF-8
Wsparcie protokołu WCCP dla Linuksa.

%package -n kernel-smp-net-%{_orig_name}
Summary:	Kernel module for WCCP protocol
Summary(pl.UTF-8):   Moduł kernela do obsługi protokołu WCCP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-%{_orig_name}
WCCP protocol support for Linux SMP.

%description -n kernel-smp-net-%{_orig_name} -l pl.UTF-8
Wsparcie protokołu WCCP dla Linuksa SMP.

%prep
%setup -q -n %{_orig_name}-%{version}

%build
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
        exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} clean modules \
    EXTRA_CFLAGS="-I../include -DFUSE_VERSION='1.1'" \
    RCS_FIND_IGNORE="-name '*.ko' -o" \
    M=$PWD O=$PWD \
    %{?with_verbose:V=1}
    mv %{_orig_name}.ko %{_orig_name}-$cfg.ko
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
cp %{_orig_name}-up.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/%{_orig_name}.ko
cp %{_orig_name}-smp.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/%{_orig_name}.ko

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-%{_orig_name}
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-%{_orig_name}
%depmod %{_kernel_ver}smp

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*

%files -n kernel-smp-net-%{_orig_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
