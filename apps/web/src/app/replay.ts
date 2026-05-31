export interface ReplayApiResponse {
    ok: boolean;
    runId: string;
    newRunId: string;
    command: string;
    args: string[];
    stdout: string;
    stderr: string;
    exitCode: number;
    bundleJson: string;
    error?: string;
}

/**
 * Invokes the replay API for a source run and returns the queued replay run id.
 */
export async function simulateSeedReplay(sourceRunId: string): Promise<{ newRunId: string }> {
    const response = await fetch(`/api/runs/${encodeURIComponent(sourceRunId)}/replay`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
        },
    });

    const payload = (await response.json()) as Partial<ReplayApiResponse>;

    if (!response.ok || !payload.ok || typeof payload.newRunId !== 'string') {
        throw new Error(
            typeof payload.error === 'string'
                ? payload.error
                : `Replay request failed with HTTP ${response.status}`,
        );
    }

    return { newRunId: payload.newRunId };
}
