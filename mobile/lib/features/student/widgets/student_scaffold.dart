import 'package:flutter/material.dart';
import '../../../core/theme/student_palette.dart';

/// Bottom nav shell — Home, Courses, Schedule, Results, Profile (mockup).
class StudentShell extends StatelessWidget {
  const StudentShell({
    super.key,
    required this.selectedIndex,
    required this.onTabSelected,
    required this.body,
  });

  final int selectedIndex;
  final ValueChanged<int> onTabSelected;
  final Widget body;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: StudentPalette.surface,
      body: body,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: StudentPalette.white,
          border: Border(top: BorderSide(color: StudentPalette.cardBorder, width: 0.5)),
        ),
        child: NavigationBar(
          height: 64,
          backgroundColor: StudentPalette.white,
          elevation: 0,
          selectedIndex: selectedIndex,
          onDestinationSelected: onTabSelected,
          indicatorColor: StudentPalette.indigo.withValues(alpha: 0.12),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.home_outlined, color: StudentPalette.textMuted),
              selectedIcon: Icon(Icons.home_rounded, color: StudentPalette.indigo),
              label: 'Home',
            ),
            NavigationDestination(
              icon: Icon(Icons.menu_book_outlined, color: StudentPalette.textMuted),
              selectedIcon: Icon(Icons.menu_book_rounded, color: StudentPalette.indigo),
              label: 'Courses',
            ),
            NavigationDestination(
              icon: Icon(Icons.calendar_month_outlined, color: StudentPalette.textMuted),
              selectedIcon: Icon(Icons.calendar_month_rounded, color: StudentPalette.indigo),
              label: 'Schedule',
            ),
            NavigationDestination(
              icon: Icon(Icons.bar_chart_outlined, color: StudentPalette.textMuted),
              selectedIcon: Icon(Icons.bar_chart_rounded, color: StudentPalette.indigo),
              label: 'Results',
            ),
            NavigationDestination(
              icon: Icon(Icons.person_outline, color: StudentPalette.textMuted),
              selectedIcon: Icon(Icons.person_rounded, color: StudentPalette.indigo),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}
