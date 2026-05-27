import 'package:flutter/material.dart';
import 'student_palette.dart';

class AppTheme {
  static final light = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: StudentPalette.teal,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: StudentPalette.profileBg,
  );

  static final dark = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: StudentPalette.bgDark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: StudentPalette.teal,
      brightness: Brightness.dark,
      primary: StudentPalette.mint,
      surface: StudentPalette.bgDark,
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: StudentPalette.bgDark,
      indicatorColor: StudentPalette.teal.withValues(alpha: 0.25),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: StudentPalette.mint, fontSize: 12);
        }
        return TextStyle(color: Colors.white.withValues(alpha: 0.45), fontSize: 12);
      }),
    ),
  );
}
