import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/student_courses_tab.dart';
import 'screens/student_fees_tab.dart';
import 'screens/student_home_tab.dart';
import 'screens/student_profile_tab.dart';
import 'screens/student_results_tab.dart';
import 'screens/student_study_hub_tab.dart';
import 'widgets/student_scaffold.dart';
import '../../core/theme/student_palette.dart';

class StudentDashboard extends ConsumerStatefulWidget {
  const StudentDashboard({super.key});

  @override
  ConsumerState<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends ConsumerState<StudentDashboard> {
  int _index = 0;

  void _openProfile() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => const Scaffold(
          backgroundColor: StudentPalette.profileBg,
          body: SafeArea(child: StudentProfileTab()),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      StudentHomeTab(onNavigate: (i) => setState(() => _index = i), onProfileTap: _openProfile),
      const StudentCoursesTab(),
      const StudentFeesTab(),
      const StudentResultsTab(),
      const StudentStudyHubTab(),
    ];

    return StudentShell(
      selectedIndex: _index,
      onTabSelected: (i) => setState(() => _index = i),
      onProfileTap: _openProfile,
      body: IndexedStack(index: _index, children: pages),
    );
  }
}
