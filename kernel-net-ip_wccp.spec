%define		_kernel_ver	%(grep UTS_RELEASE %{_kernelsrcdir}/include/linux/version.h 2>/dev/null | cut -d'"' -f2)
%define		_kernel_ver_str	%(echo %{_kernel_ver} | sed s/-/_/g)
%define		smpstr		%{?_with_smp:-smp}
%define		smp		%{?_with_smp:1}%{!?_with_smp:0}

Summary:	Kernel module for WCCP protocol
Summary(pl):	Modu³ kernela do obs³ugi protoko³u WCCP
%define		_orig_name	ip_wccp
Name:		kernel%{smpstr}-net-%{_orig_name}
Version:	0.1
Release:	1@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Group(de):	Grundsätzlich/Kern
Group(pl):	Podstawowe/J±dro
Source0:	http://www.squid-cache.org/WCCP-support/Linux/%{_orig_name}.c
BuildRequires:	kernel-headers
%{?_with_smp:Obsoletes: kernel-net-%{_orig_name}}
Prereq:		/sbin/depmod
Conflicts:	kernel < %{_kernel_ver}, kernel > %{_kernel_ver}
Conflicts:	kernel-%{?_with_smp:up}%{!?_with_smp:smp}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WCCP protocol support for Linux.

%description -l pl
Wsparcie protoko³u WCCP dla Linuxa.

%prep
%setup -q -T -c
install %{SOURCE0} .

%build
%if %{smp}
SMP="-D__KERNEL_SMP=1"
%endif
kgcc -D__KERNEL__ -I%{_kernelsrcdir}/include -Wall -Wstrict-prototypes -fomit-frame-pointer \
	-fno-strict-aliasing -pipe -fno-strength-reduce %{rpmcflags} -DMODULE -DMODVERSIONS \
	-include %{_kernelsrcdir}/include/linux/modversions.h $SMP -c %{_orig_name}.c

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/ipv4
cp %{_orig_name}.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/ipv4

%clean 
rm -rf $RPM_BUILD_ROOT

%post
/sbin/depmod -a

%postun
/sbin/depmod -a

%files
%defattr(644,root,root,755)
/lib/modules/*/ipv4/*
