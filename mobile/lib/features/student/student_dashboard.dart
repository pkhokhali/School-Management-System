import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/providers/auth_provider.dart';
import 'notices_screen.dart';
import 'fees_screen.dart';
import 'qr_display_screen.dart';

class StudentDashboard extends ConsumerStatefulWidget {
  const StudentDashboard({super.key});

  @override
  ConsumerState<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends ConsumerState<StudentDashboard> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      const _OverviewTab(),
      const NoticesScreen(),
      const FeesScreen(),
      const QRDisplayScreen(),
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student'),
        actions: [
          IconButton(icon: const Icon(Icons.person), onPressed: () => context.push('/profile')),
        ],
      ),
      body: pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.notifications), label: 'Notices'),
          NavigationDestination(icon: Icon(Icons.payments), label: 'Fees'),
          NavigationDestination(icon: Icon(Icons.qr_code), label: 'My QR'),
        ],
      ),
    );
  }
}

class _OverviewTab extends ConsumerWidget {
  const _OverviewTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(child: ListTile(title: Text('Welcome, ${user?.fullName}'), subtitle: Text(user?.email ?? ''))),
        const ListTile(title: Text('Attendance'), subtitle: Text('View monthly summary in portal')),
        const ListTile(title: Text('Results'), subtitle: Text('Available when published')),
      ],
    );
  }
}
