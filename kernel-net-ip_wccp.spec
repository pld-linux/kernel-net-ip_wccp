#
# Conditional build:
# _without_dist_kernel          without distribution kernel
#
%define         _orig_name      ip_wccp
%define		_kernel24	%(echo %{_kernel_ver} | grep -qv '2\.4\.' ; echo $?)

Summary:	Kernel module for WCCP protocol
Summary(pl):	Modu³ kernela do obs³ugi protoko³u WCCP
Name:		kernel-net-%{_orig_name}
Version:	0.2
%define	_rel	1
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.squid-cache.org/WCCP-support/Linux/%{_orig_name}.c
Source1:	http://ftp.yars.free.net/pub/software/unix/platforms/linux/kernel/drivers/ip_wccp-for2.6.0.c
%{!?_without_dist_kernel:BuildRequires:	kernel-headers >= 2.4.0}
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
%{!?_without_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WCCP protocol support for Linux.

%description -l pl
Wsparcie protoko³u WCCP dla Linuksa.

%package -n kernel-smp-net-%{_orig_name}
Summary:	Kernel module for WCCP protocol
Summary(pl):	Modu³ kernela do obs³ugi protoko³u WCCP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{!?_without_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-%{_orig_name}
WCCP protocol support for Linux SMP.

%description -n kernel-smp-net-%{_orig_name} -l pl
Wsparcie protoko³u WCCP dla Linuksa SMP.

%prep
%setup -q -T -c
%if %{_kernel24}
install %{SOURCE0} %{_orig_name}.c
%else
install %{SOURCE1} %{_orig_name}.c
%endif

%build
%if %{_kernel24}
%{kgcc} -D__KERNEL__ -DMODULE -D__SMP__ -DCONFIG_X86_LOCAL_APIC -I%{_kernelsrcdir}/include -Wall \
	-Wstrict-prototypes -fomit-frame-pointer -fno-strict-aliasing -pipe -fno-strength-reduce \
%ifarch %{ix86}
	-I%{_kernelsrcdir}/include/asm-i386/mach-default \
%endif
	%{rpmcflags} -c %{_orig_name}.c

mv -f %{_orig_name}.o %{_orig_name}smp.o

%{kgcc} -D__KERNEL__ -DMODULE -I%{_kernelsrcdir}/include -Wall -Wstrict-prototypes \
	-fomit-frame-pointer -fno-strict-aliasing -pipe -fno-strength-reduce \
%ifarch %{ix86}
        -I%{_kernelsrcdir}/include/asm-i386/mach-default \
%endif
	%{rpmcflags} -c %{_orig_name}.c
%else
ln -sf %{_kernelsrcdir}/config-up .config
echo 'obj-m := %{_orig_name}.o' > Makefile
%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 modules
mv -f %{_orig_name}.ko %{_orig_name}smp.ko-done
ln -sf %{_kernelsrcdir}/config-smp .config
%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 clean modules
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
%if %{_kernel24}
cp %{_orig_name}.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/%{_orig_name}.o
cp %{_orig_name}smp.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/%{_orig_name}.o
%else
cp %{_orig_name}.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/%{_orig_name}.ko
cp %{_orig_name}smp.ko-done $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/%{_orig_name}.ko
%endif

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
