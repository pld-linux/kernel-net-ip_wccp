
# conditional build
# _without_dist_kernel          without distribution kernel

%define		_kernel_ver	%(grep UTS_RELEASE %{_kernelsrcdir}/include/linux/version.h 2>/dev/null | cut -d'"' -f2)
%define		_kernel_ver_str	%(echo %{_kernel_ver} | sed s/-/_/g)
%define         _orig_name      ip_wccp
%define		_rel	6

Summary:	Kernel module for WCCP protocol
Summary(pl):	Modu� kernela do obs�ugi protoko�u WCCP
Name:		kernel-net-%{_orig_name}
Version:	0.1
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.squid-cache.org/WCCP-support/Linux/%{_orig_name}.c
%{!?_without_dist_kernel:BuildRequires:         kernel-headers}
BuildRequires:	%{kgcc_package}
Obsoletes:	kernel-smp-net-%{_orig_name}
Prereq:		/sbin/depmod
%{!?_without_dist_kernel:%requires_releq_kernel_up}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WCCP protocol support for Linux.

%description -l pl
Wsparcie protoko�u WCCP dla Linuksa.

%package -n kernel-smp-net-%{_orig_name}
Summary:	Kernel module for WCCP protocol
Summary(pl):	Modu� kernela do obs�ugi protoko�u WCCP
Release:	%{_rel}@%{_kernel_ver_str}
%{!?_without_dist_kernel:%requires_releq_kernel_smp}
Group:		Base/Kernel
Obsoletes:	kernel-net-%{_orig_name}
Prereq:		/sbin/depmod

%description -n kernel-smp-net-%{_orig_name}
WCCP protocol support for Linux SMP.

%description -n kernel-smp-net-%{_orig_name} -l pl
Wsparcie protoko�u WCCP dla Linuksa SMP.

%prep
%setup -q -T -c
install %{SOURCE0} .

%build
%{kgcc} -D__KERNEL__ -DMODULE -D__SMP__ -DCONFIG_X86_LOCAL_APIC -I%{_kernelsrcdir}/include -Wall \
	-Wstrict-prototypes -fomit-frame-pointer -fno-strict-aliasing -pipe -fno-strength-reduce \
	%{rpmcflags} -c %{_orig_name}.c

mv -f %{_orig_name}.o %{_orig_name}smp.o

%{kgcc} -D__KERNEL__ -DMODULE -I%{_kernelsrcdir}/include -Wall -Wstrict-prototypes \
	-fomit-frame-pointer -fno-strict-aliasing -pipe -fno-strength-reduce \
	%{rpmcflags} -c %{_orig_name}.c

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/ipv4
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/ipv4
cp %{_orig_name}.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/ipv4
cp %{_orig_name}smp.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/ipv4/%{_orig_name}.o

%clean 
rm -rf $RPM_BUILD_ROOT

%post
/sbin/depmod -a

%postun
/sbin/depmod -a

%post -n kernel-smp-net-%{_orig_name}
/sbin/depmod -a

%postun -n kernel-smp-net-%{_orig_name}
/sbin/depmod -a

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/ipv4/*

%files -n kernel-smp-net-%{_orig_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/ipv4/*
