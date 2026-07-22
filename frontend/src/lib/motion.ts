"use client";

import { motion, type Variants } from "motion/react";
import { motion as tokens } from "@/lib/design-system";

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: tokens.base, ease: tokens.ease },
  },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: tokens.base, ease: tokens.ease } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: tokens.base, ease: tokens.ease },
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.04 },
  },
};

export const listItem: Variants = {
  hidden: { opacity: 0, y: 12, scale: 0.98 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: tokens.base, ease: tokens.ease },
  },
};

export const MotionDiv = motion.div;
export const MotionSection = motion.section;
export const MotionLi = motion.li;
export const MotionButton = motion.button;
export const MotionHeader = motion.header;
