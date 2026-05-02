import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getJob, updateJob, getCategories } from "../../lib/api";
import JobForm from "../../components/JobForm";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

export default function EditJob() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getJob(id), getCategories()])
      .then(([j, c]) => { setJob(j.data); setCategories(c.data || []); })
      .catch(() => toast.error("Gagal memuat data"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (data) => {
    await updateJob(id, data);
    toast.success("Lowongan berhasil diperbarui!");
    navigate("/employer/jobs");
  };

  if (loading) return <div className="max-w-3xl mx-auto px-4 py-12"><Spinner center /></div>;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-forgotten-blue mb-6">Edit Lowongan</h1>
      {job && <JobForm initialData={job} categories={categories} onSubmit={handleSubmit} submitLabel="Simpan Perubahan" />}
    </div>
  );
}
