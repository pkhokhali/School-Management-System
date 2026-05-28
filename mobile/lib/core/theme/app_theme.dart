import 'package:flutter/material.dart';
import 'student_palette.dart';

class AppTheme {
  static final light = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: StudentPalette.indigo,
      brightness: Brightness.light,
      primary: StudentPalette.indigo,
    ),
    scaffoldBackgroundColor: StudentPalette.surface,
    appBarTheme: const AppBarTheme(
      backgroundColor: StudentPalette.navy,
      foregroundColor: Colors.white,
      elevation: 0,
    ),
  );

  static final dark = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: StudentPalette.navy,
    colorScheme: ColorScheme.fromSeed(
      seedColor: StudentPalette.indigo,
      brightness: Brightness.dark,
      primary: StudentPalette.indigo,
      surface: StudentPalette.navy,
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: StudentPalette.white,
      indicatorColor: StudentPalette.indigo.withValues(alpha: 0.12),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: StudentPalette.indigo, fontSize: 12, fontWeight: FontWeight.w600);
        }
        return const TextStyle(color: StudentPalette.textMuted, fontSize: 12);
      }),
    ),
  );
}
