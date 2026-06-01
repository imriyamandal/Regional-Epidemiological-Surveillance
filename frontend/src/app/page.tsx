"use client";

import { motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  CloudRain,
  Globe2,
  Mail,
  MapPin,
  Shield,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  { icon: Brain, title: "AI Outbreak Prediction", desc: "50+ engineered features with ensemble ML and deep learning models." },
  { icon: Shield, title: "Early Warning System", desc: "Green to Red alert levels with automated notifications." },
  { icon: MapPin, title: "Geographic Intelligence", desc: "District-level heatmaps and hotspot detection across India." },
  { icon: CloudRain, title: "Climate-Aware Analysis", desc: "Temperature, rainfall, humidity, and LAI integrated forecasting." },
  { icon: BarChart3, title: "Case Forecasting", desc: "1–12 month horizons with confidence intervals." },
  { icon: Activity, title: "Explainable AI", desc: "SHAP, feature importance, and driver analysis for trust." },
];

const stats = [
  { label: "Districts Monitored", value: "700+" },
  { label: "Diseases Tracked", value: "6+" },
  { label: "ML Models", value: "15+" },
  { label: "Features Engineered", value: "50+" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <Activity className="h-8 w-8 text-cyan-400" />
          <span className="text-xl font-bold">DOPEWIS</span>
        </div>
        <div className="flex gap-3">
          <Link href="/login">
            <Button variant="outline" className="border-slate-600 text-white hover:bg-slate-800">
              Sign in
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button className="bg-cyan-500 hover:bg-cyan-600">Launch Platform</Button>
          </Link>
        </div>
      </nav>

      <section className="gradient-hero relative overflow-hidden px-6 pb-24 pt-16">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(6,182,212,0.25),transparent_50%)]" />
        <div className="relative mx-auto max-w-5xl text-center">
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-4 inline-block rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-300"
          >
            Disease Outbreak Prediction & Early Warning Intelligence
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-balance text-4xl font-bold tracking-tight md:text-6xl"
          >
            Predict outbreaks before they become epidemics
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, transition: { delay: 0.2 } }}
            className="mx-auto mt-6 max-w-2xl text-lg text-slate-300"
          >
            Enterprise-grade AI surveillance for WHO, government health departments, and disease
            control centers — forecasting cases, identifying hotspots, and delivering explainable
            intelligence.
          </motion.p>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, transition: { delay: 0.4 } }}
            className="mt-10 flex flex-wrap justify-center gap-4"
          >
            <Link href="/dashboard">
              <Button size="lg" className="bg-cyan-500 hover:bg-cyan-600">
                Open Dashboard <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="border-slate-500 text-white">
                Request Demo Access
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-20">
        <h2 className="text-center text-3xl font-bold">Platform Capabilities</h2>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Card className="border-slate-800 bg-slate-900/50 h-full">
                <CardContent className="p-6">
                  <f.icon className="h-10 w-10 text-cyan-400" />
                  <h3 className="mt-4 text-lg font-semibold text-white">{f.title}</h3>
                  <p className="mt-2 text-sm text-slate-400">{f.desc}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="border-y border-slate-800 bg-slate-900/50 py-16">
        <div className="mx-auto grid max-w-5xl grid-cols-2 gap-8 px-6 md:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <p className="text-3xl font-bold text-cyan-400">{s.value}</p>
              <p className="mt-1 text-sm text-slate-400">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-20">
        <h2 className="text-center text-3xl font-bold">Architecture</h2>
        <Card className="mt-10 border-slate-800 bg-slate-900/50">
          <CardContent className="p-8 font-mono text-sm text-slate-300">
            <pre className="overflow-x-auto">{`┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Next.js    │────▶│   FastAPI    │────▶│  PostgreSQL   │
│  Dashboard  │     │   REST API   │     │  Surveillance │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────▼───────┐     ┌─────────────────┐
                    │ ML Pipeline  │────▶│     MLflow      │
                    │ XGB/LGB/LSTM │     │ Model Registry  │
                    └──────────────┘     └─────────────────┘`}</pre>
          </CardContent>
        </Card>
      </section>

      <section className="mx-auto max-w-xl px-6 pb-24 text-center">
        <Globe2 className="mx-auto h-12 w-12 text-cyan-400" />
        <h2 className="mt-4 text-2xl font-bold">Contact Public Health Team</h2>
        <p className="mt-2 text-slate-400">health@dopewis.intelligence</p>
        <a href="mailto:health@dopewis.intelligence" className="mt-4 inline-flex items-center gap-2 text-cyan-400">
          <Mail className="h-4 w-4" /> Get in touch
        </a>
      </section>

      <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} DOPEWIS — Regional Epidemiological Surveillance Platform
      </footer>
    </div>
  );
}
