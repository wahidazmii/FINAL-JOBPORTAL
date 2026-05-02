import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { MapPin, Globe, Building2, Users } from "lucide-react";
import { getCompany } from "../lib/api";
import JobCard from "../components/JobCard";
import Spinner from "../components/ui/Spinner";

export default function CompanyPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCompany(slug)
      .then(({ data }) => setData(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-12"><Spinner center /></div>;
  if (!data) return <div className="text-center py-20 text-gray-400">Perusahaan tidak ditemukan</div>;

  const { company, jobs } = data;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      {/* Header */}
      <div className="card p-6 mb-6">
        <div className="flex items-center gap-5">
          {company.logo_url ? (
            <img src={company.logo_url} alt={company.name} className="w-16 h-16 rounded-xl object-cover" />
          ) : (
            <div className="w-16 h-16 rounded-xl bg-fountain-mint flex items-center justify-center text-jungle-teal font-bold text-xl">
              {company.name?.[0]}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-forgotten-blue">{company.name}</h1>
            <div className="flex flex-wrap gap-3 mt-1 text-sm text-gray-500">
              {company.industry && <span className="flex items-center gap-1"><Building2 size={14} /> {company.industry}</span>}
              {company.location && <span className="flex items-center gap-1"><MapPin size={14} /> {company.location}</span>}
              {company.size && <span className="flex items-center gap-1"><Users size={14} /> {company.size} karyawan</span>}
              {company.website && (
                <a href={company.website} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-jungle-teal hover:underline">
                  <Globe size={14} /> Website
                </a>
              )}
            </div>
          </div>
        </div>
        {company.description && (
          <p className="text-sm text-gray-600 mt-4 leading-relaxed">{company.description}</p>
        )}
      </div>

      {/* Jobs */}
      <h2 className="font-bold text-forgotten-blue mb-4">{jobs?.length || 0} Lowongan Aktif</h2>
      {jobs?.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => <JobCard key={job.id} job={job} />)}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400 text-sm">
          Tidak ada lowongan aktif saat ini
        </div>
      )}
    </div>
  );
}
