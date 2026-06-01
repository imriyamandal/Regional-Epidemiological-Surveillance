"use client";

import { useState } from "react";
import { Activity } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@dopewis.health");
  const [password, setPassword] = useState("Admin@12345");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await api<{ access_token: string }>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-cyan-950 p-4">
      <Card className="w-full max-w-md border-slate-800 bg-slate-900/90">
        <CardHeader className="text-center">
          <Activity className="mx-auto h-10 w-10 text-cyan-400" />
          <CardTitle className="mt-2 text-white">Sign in to DOPEWIS</CardTitle>
          <p className="text-sm text-slate-400">Public health intelligence platform</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-slate-300">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                required
              />
            </div>
            <div>
              <label className="text-sm text-slate-300">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                required
              />
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <Button type="submit" className="w-full bg-cyan-600" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
          <p className="mt-4 text-center text-xs text-slate-500">
            Demo: admin@dopewis.health / Admin@12345
          </p>
          <Link href="/signup" className="mt-2 block text-center text-sm text-cyan-400 hover:underline">
            Create an account
          </Link>
          <Link href="/" className="mt-2 block text-center text-sm text-slate-500 hover:underline">
            Back to home
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
