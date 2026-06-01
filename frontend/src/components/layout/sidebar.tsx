"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  FileText,
  LayoutDashboard,
  Map,
  Settings,
  Shield,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/forecasting", label: "Forecasting", icon: BarChart3 },
  { href: "/risk", label: "Risk Analysis", icon: Shield },
  { href: "/map", label: "Outbreak Map", icon: Map },
  { href: "/explainability", label: "Explainable AI", icon: Sparkles },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/alerts", label: "Alerts", icon: AlertTriangle },
  { href: "/admin", label: "Admin", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white/90 dark:border-slate-800 dark:bg-slate-950/90 lg:flex lg:flex-col">
      <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6 dark:border-slate-800">
        <Activity className="h-7 w-7 text-cyan-500" />
        <div>
          <p className="text-sm font-bold text-slate-900 dark:text-white">DOPEWIS</p>
          <p className="text-[10px] text-slate-500">Early Warning Intelligence</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              pathname === href
                ? "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-cyan-300"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-900"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
