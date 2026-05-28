import { NextResponse } from 'next/server';
import { buildMockRuns } from '@/app/mockRuns';

export async function GET(
    _request: Request,
    { params }: { params: Promise<{ id: string }> },
) {
    const { id } = await params;
    const run = buildMockRuns().find((r) => r.id === id);
    if (!run) {
        return NextResponse.json({ error: 'Run not found' }, { status: 404 });
    }
    return NextResponse.json(run);
}
