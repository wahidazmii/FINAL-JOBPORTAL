// Format IDR currency
export function formatIDR(amount) {
  if (!amount) return "—";
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

// Format relative time
export function timeAgo(isoString) {
  if (!isoString) return "—";
  const diff = Date.now() - new Date(isoString).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Baru saja";
  if (minutes < 60) return `${minutes} menit lalu`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} jam lalu`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} hari lalu`;
  const months = Math.floor(days / 30);
  return `${months} bulan lalu`;
}

// Format date
export function formatDate(isoString) {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleDateString("id-ID", {
    day: "numeric", month: "long", year: "numeric"
  });
}

// Employment type labels
export const EMPLOYMENT_LABELS = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Kontrak",
  internship: "Magang",
  freelance: "Freelance",
};

// Work mode labels
export const WORK_MODE_LABELS = {
  onsite: "Onsite",
  remote: "Remote",
  hybrid: "Hybrid",
};

// Experience level labels
export const EXPERIENCE_LABELS = {
  entry: "Entry Level",
  junior: "Junior",
  mid: "Mid Level",
  senior: "Senior",
  lead: "Lead",
};

// Application status labels and colors
export const APP_STATUS = {
  applied: { label: "Dilamar", color: "bg-blue-50 text-blue-700" },
  reviewing: { label: "Sedang Diulas", color: "bg-yellow-50 text-yellow-700" },
  interview: { label: "Interview", color: "bg-purple-50 text-purple-700" },
  rejected: { label: "Ditolak", color: "bg-red-50 text-red-700" },
  hired: { label: "Diterima", color: "bg-green-50 text-green-700" },
};

// Job status labels
export const JOB_STATUS = {
  draft: { label: "Draft", color: "bg-gray-100 text-gray-600" },
  published: { label: "Aktif", color: "bg-green-50 text-green-700" },
  paused: { label: "Dijeda", color: "bg-yellow-50 text-yellow-700" },
  closed: { label: "Ditutup", color: "bg-red-50 text-red-700" },
};

// Score color helper
export function scoreColor(score) {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-500";
}

// Truncate text
export function truncate(text, n = 100) {
  if (!text) return "";
  return text.length <= n ? text : text.slice(0, n) + "…";
}
