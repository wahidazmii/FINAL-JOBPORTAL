import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createJob, getCategories } from "../../lib/api";
import JobForm from "../../components/JobForm";
import { toast } from "react-toastify";

export default function PostJob() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    getCategories().then(({ data }) => setCategories(data || [])).catch(() => {});
  }, []);

  const handleSubmit = async (data) => {
    await createJob(data);
    toast.success("Lowongan berhasil diposting! 🎉");
    navigate("/employer/jobs");
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-forgotten-blue mb-6">Post Lowongan Baru</h1>
      <JobForm categories={categories} onSubmit={handleSubmit} submitLabel="Post Lowongan" />
    </div>
  );
}
