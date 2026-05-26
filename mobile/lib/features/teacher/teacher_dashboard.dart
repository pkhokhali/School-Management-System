import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'attendance_scan_screen.dart';
import 'bulk_attendance_screen.dart';

class TeacherDashboard extends StatefulWidget {
  const TeacherDashboard({super.key});

  @override
  State<TeacherDashboard> createState() => _TeacherDashboardState();
}

class _TeacherDashboardState extends State<TeacherDashboard> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Teacher'),
        actions: [IconButton(icon: const Icon(Icons.person), onPressed: () => context.push('/profile'))],
      ),
      body: _index == 0
          ? const _TeacherHome()
          : _index == 1
              ? const AttendanceScanScreen()
              : const BulkAttendanceScreen(),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.qr_code_scanner), label: 'Scan QR'),
          NavigationDestination(icon: Icon(Icons.list), label: 'Bulk Mark'),
        ],
      ),
    );
  }
}

class _TeacherHome extends StatelessWidget {
  const _TeacherHome();

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: const [
        ListTile(
          title: Text('Mark Attendance'),
          subtitle: Text(
            'Scan tab: pick your class (batch · course · period), scan QR. Registers open automatically.',
          ),
        ),
        ListTile(
          title: Text('Enter Marks'),
          subtitle: Text('Results module when enabled'),
        ),
      ],
    );
  }
}
