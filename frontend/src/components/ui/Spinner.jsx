export default function Spinner({ size = "md", center = false }) {
  const sz = { sm: "w-5 h-5", md: "w-8 h-8", lg: "w-12 h-12" }[size] || "w-8 h-8";
  return (
    <div className={center ? "flex justify-center py-12" : ""}>
      <div className={`${sz} spinner`} />
    </div>
  );
}
