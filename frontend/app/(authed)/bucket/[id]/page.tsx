import BucketView from "./BucketView";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <BucketView bucketId={id} />;
}
