import 'package:flutter/material.dart';

/// Brand palette aligned with student_mobile_app_ux.html
abstract final class StudentPalette {
  static const bgDark = Color(0xFF0F1E2E);
  static const bgCard = Color(0x1AFFFFFF);
  static const textPrimary = Color(0xFFE2EFF8);
  static const textMuted = Color(0x73FFFFFF);
  static const teal = Color(0xFF028090);
  static const mint = Color(0xFF02C39A);
  static const heroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [teal, mint],
  );

  static const profileBg = Color(0xFFF4F7FB);
  static const profileText = Color(0xFF1E3A4F);
  static const profileMuted = Color(0xFF94A3B8);

  static Color attendanceColor(double pct) {
    if (pct >= 75) return const Color(0xFF4ADE80);
    if (pct >= 60) return const Color(0xFFFBBF24);
    return const Color(0xFFF87171);
  }

  static Color progressBarColor(double pct) {
    if (pct >= 75) return const Color(0xFF22C55E);
    if (pct >= 60) return const Color(0xFFF0A500);
    return const Color(0xFFEF4444);
  }
}
