Name:           wifiman-desktop
Version:        %{_version}
Release:        1%{?dist}
Summary:        Ubiquiti WiFiman Desktop (Fedora Repack)
License:        Proprietary
BuildArch:      x86_64
AutoReqProv:    no
BuildRequires: systemd-rpm-macros

%description
WiFiman Desktop for Fedora. Includes Teleport (WireGuard) fixes.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/lib/wifiman-desktop
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor
mkdir -p %{buildroot}%{_unitdir}

# Kopiowanie binarki GUI
cp %{_ws}/usr/bin/wifiman-desktop %{buildroot}/usr/bin/

# Kopiowanie całej zawartości katalogu aplikacji
cp -a %{_ws}/usr/lib/wifiman-desktop/. %{buildroot}/usr/lib/wifiman-desktop/

# Reszta zasobów
cp -r %{_ws}/usr/share/applications/* %{buildroot}/usr/share/applications/
cp -r %{_ws}/usr/share/icons/hicolor/* %{buildroot}/usr/share/icons/hicolor/

# Opcjonalny plik polityki SELinux, jeśli istnieje
if [ -f %{_ws}/usr/lib/wifiman-desktop/wifiman_policy.pp ]; then
  cp %{_ws}/usr/lib/wifiman-desktop/wifiman_policy.pp %{buildroot}/usr/lib/wifiman-desktop/wifiman_policy.pp
fi

# Przeniesienie serwisu
mv %{buildroot}/usr/lib/wifiman-desktop/wifiman-desktop.service %{buildroot}%{_unitdir}/

%post
# 1. SELinux: Rejestracja etykiet
semanage fcontext -a -t unconfined_exec_t "/usr/lib/wifiman-desktop/wifiman-desktopd" 2>/dev/null || :
semanage fcontext -a -t unconfined_exec_t "/usr/lib/wifiman-desktop/wireguard-go" 2>/dev/null || :
restorecon -Rv /usr/lib/wifiman-desktop/ >/dev/null 2>&1 || :
if [ -f /usr/lib/wifiman-desktop/wifiman_policy.pp ]; then
  semodule -i /usr/lib/wifiman-desktop/wifiman_policy.pp 2>/dev/null || :
fi

# 2. Capabilities dla Teleportu
setcap 'cap_net_admin,cap_net_raw+ep' /usr/lib/wifiman-desktop/wifiman-desktopd 2>/dev/null || :
setcap 'cap_net_admin,cap_net_raw+ep' /usr/lib/wifiman-desktop/wireguard-go 2>/dev/null || :

# 3. Systemd: Rejestracja i automatyczny start
%systemd_post wifiman-desktop.service
/usr/bin/systemctl enable --now wifiman-desktop.service >/dev/null 2>&1 || :

%preun
%systemd_preun wifiman-desktop.service

%postun
%systemd_postun_with_restart wifiman-desktop.service

%files
%attr(0755, root, root) /usr/bin/wifiman-desktop
/usr/lib/wifiman-desktop/
%{_unitdir}/wifiman-desktop.service
/usr/share/applications/wifiman-desktop.desktop
/usr/share/icons/hicolor/*/apps/wifiman-desktop.png
%ghost %config(noreplace) /usr/lib/wifiman-desktop/wifiman_policy.pp

%changelog
* Sun Feb 15 2026 Dawid <dawid@example.com> - 1.2.8-1
- Fix build paths and make SELinux policy optional
