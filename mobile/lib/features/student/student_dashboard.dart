import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/student_courses_tab.dart';
import 'screens/student_fees_tab.dart';
import 'screens/student_home_tab.dart';
import 'screens/student_profile_tab.dart';
import 'screens/student_results_tab.dart';
import 'screens/student_schedule_tab.dart';
import 'widgets/student_scaffold.dart';
import '../../core/theme/student_palette.dart';

class StudentDashboard extends ConsumerStatefulWidget {
  const StudentDashboard({super.key});

  @override
  ConsumerState<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends ConsumerState<StudentDashboard> {
  int _index = 0;

  void _goToTab(int i) => setState(() => _index = i);

  void _openFees() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => const Scaffold(
          backgroundColor: StudentPalette.surface,
          body: SafeArea(child: StudentFeesTab()),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      StudentHomeTab(
        onNavigate: _goToTab,
        onOpenFees: _openFees,
        onProfileTap: () => _goToTab(4),
      ),
      const StudentCoursesTab(),
      const StudentScheduleTab(),
      const StudentResultsTab(),
      const StudentProfileTab(),
    ];

    return StudentShell(
      selectedIndex: _index,
      onTabSelected: _goToTab,
      body: IndexedStack(index: _index, children: pages),
    );
  }
}
