import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/student_palette.dart';
import 'student_ui.dart';

class StudentShell extends ConsumerWidget {
  const StudentShell({
    super.key,
    required this.selectedIndex,
    required this.onTabSelected,
    required this.body,
    this.onProfileTap,
    this.title,
    this.subtitle,
    this.trailing,
    this.lightMode = false,
  });

  final int selectedIndex;
  final ValueChanged<int> onTabSelected;
  final VoidCallback? onProfileTap;
  final Widget body;
  final String? title;
  final String? subtitle;
  final Widget? trailing;
  final bool lightMode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider);
    final bg = lightMode ? StudentPalette.profileBg : StudentPalette.bgDark;

    return Scaffold(
      backgroundColor: bg,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (title != null)
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            title!,
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w600,
                              color: lightMode ? StudentPalette.profileText : StudentPalette.textPrimary,
                            ),
                          ),
                          if (subtitle != null)
                            Text(
                              subtitle!,
                              style: TextStyle(
                                fontSize: 12,
                                color: lightMode ? StudentPalette.profileMuted : StudentPalette.textMuted,
                              ),
                            ),
                        ],
                      ),
                    ),
                    if (trailing != null) trailing!,
                    if (!lightMode) ...[
                      const SizedBox(width: 8),
                      IconButton(
                        onPressed: onProfileTap ?? () => context.push('/profile'),
                        icon: CircleAvatar(
                          radius: 18,
                          backgroundColor: StudentPalette.mint.withValues(alpha: 0.85),
                          child: Text(
                            initials(user?.fullName ?? ''),
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            Expanded(child: body),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: lightMode ? Colors.white : StudentPalette.bgDark.withValues(alpha: 0.97),
          border: Border(
            top: BorderSide(
              color: lightMode
                  ? const Color(0xFFE2E8F0)
                  : Colors.white.withValues(alpha: 0.08),
            ),
          ),
        ),
        child: NavigationBar(
          height: 64,
          backgroundColor: Colors.transparent,
          elevation: 0,
          selectedIndex: selectedIndex,
          onDestinationSelected: onTabSelected,
          indicatorColor: StudentPalette.teal.withValues(alpha: 0.25),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          destinations: [
            _nav(Icons.home_rounded, 'Home', lightMode),
            _nav(Icons.menu_book_rounded, 'Courses', lightMode),
            _nav(Icons.payments_rounded, 'Fees', lightMode),
            _nav(Icons.bar_chart_rounded, 'Results', lightMode),
            _nav(Icons.school_rounded, 'Study', lightMode),
          ],
        ),
      ),
    );
  }

  NavigationDestination _nav(IconData icon, String label, bool light) {
    return NavigationDestination(
      icon: Icon(icon, color: light ? StudentPalette.profileMuted : StudentPalette.textMuted),
      selectedIcon: Icon(icon, color: StudentPalette.mint),
      label: label,
    );
  }
}
