import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../../features/auth/login_screen.dart';
import '../../features/auth/role_select_screen.dart';
import '../../features/student/student_dashboard.dart';
import '../../features/teacher/teacher_dashboard.dart';
import '../../features/admin/admin_dashboard.dart';
import '../../features/shared/profile_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authProvider);
  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final loggedIn = auth != null;
      final onLogin = state.matchedLocation == '/login';
      if (!loggedIn && !onLogin) return '/login';
      if (loggedIn && onLogin) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/role-select', builder: (_, __) => const RoleSelectScreen()),
      GoRoute(path: '/home', builder: (_, __) => const _HomeRouter()),
      GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
    ],
  );
});

class _HomeRouter extends ConsumerWidget {
  const _HomeRouter();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider);
    switch (user?.role) {
      case 'teacher':
        return const TeacherDashboard();
      case 'admin_staff':
      case 'super_admin':
        return const AdminDashboard();
      default:
        return const StudentDashboard();
    }
  }
}
