import 'package:flutter/material.dart';

/// Matches student_app_all_screens.html + admin instituteBrand
abstract final class StudentPalette {
  static const navy = Color(0xFF1A1A2E);
  static const indigo = Color(0xFF4361EE);
  static const indigoLight = Color(0xFF818CF8);
  static const surface = Color(0xFFF4F6FB);
  static const cardBorder = Color(0xFFE8EAF0);
  static const textPrimary = Color(0xFF1A1A2E);
  static const textMuted = Color(0xFF94A3B8);
  static const white = Color(0xFFFFFFFF);

  static const success = Color(0xFF16A34A);
  static const successBg = Color(0xFFDCFCE7);
  static const successText = Color(0xFF166534);
  static const warning = Color(0xFFD97706);
  static const warningBg = Color(0xFFFEF3C7);
  static const warningText = Color(0xFF92400E);
  static const error = Color(0xFFDC2626);
  static const errorBg = Color(0xFFFEE2E2);
  static const errorText = Color(0xFF991B1B);
  static const info = Color(0xFF2563EB);
  static const infoBg = Color(0xFFDBEAFE);
  static const infoText = Color(0xFF1D4ED8);
  static const purple = Color(0xFF9333EA);
  static const purpleBg = Color(0xFFFDF4FF);
  static const grayBg = Color(0xFFF1F5F9);
  static const grayText = Color(0xFF475569);

  static Color progressColor(double pct) {
    if (pct >= 75) return success;
    if (pct >= 60) return warning;
    return error;
  }

  static Color attendanceColor(double pct) => progressColor(pct);
  static Color progressBarColor(double pct) => progressColor(pct);

  static const profileBg = surface;
  static const profileText = textPrimary;
  static const profileMuted = textMuted;
}
