"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function StatCard({
  title,
  value,
  change,
  icon: Icon,
  accent = "blue",
}: {
  title: string;
  value: string | number;
  change?: string;
  icon: LucideIcon;
  accent?: "blue" | "cyan" | "orange" | "red" | "green";
}) {
  const colors = {
    blue: "from-blue-500/20 to-blue-600/5 text-blue-600",
    cyan: "from-cyan-500/20 to-cyan-600/5 text-cyan-600",
    orange: "from-orange-500/20 to-orange-600/5 text-orange-600",
    red: "from-red-500/20 to-red-600/5 text-red-600",
    green: "from-emerald-500/20 to-emerald-600/5 text-emerald-600",
  };

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="overflow-hidden">
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-slate-500">{title}</p>
              <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
              {change && <p className="mt-1 text-xs text-slate-500">{change}</p>}
            </div>
            <div className={cn("rounded-xl bg-gradient-to-br p-3", colors[accent])}>
              <Icon className="h-5 w-5" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
