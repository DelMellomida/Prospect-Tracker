// These values match the Django choices. There are no API calls in the frontend.
export const statuses = ["contacted", "ongoing", "completion", "dropped"] as const;
export const sources = ["reddit", "discord", "facebook", "linkedin", "others"] as const;
export type Status = (typeof statuses)[number];
export type Source = (typeof sources)[number];
export const statusLabels: Record<Status, string> = { contacted: "Contacted", ongoing: "In progress", completion: "Completed", dropped: "Dropped" };
export const sourceLabels: Record<Source, string> = { reddit: "Reddit", discord: "Discord", facebook: "Facebook", linkedin: "LinkedIn", others: "Other" };
export interface Note {
    id: string;
    content: string;
    created_at: string;
}
export interface Prospect {
    record_id: string;
    company: string;
    status: Status;
    company_contact_no: string;
    company_email: string;
    last_date_contacted: string;
    technical_audit: string;
    source: Source;
    created_at: string;
    notes: Note[];
    follow_up: {
        date: string;
        content: string;
    } | null;
}
export type ProspectInput = Omit<Prospect, "record_id" | "created_at" | "notes">;
// Local UI activity is separate from the backend's persistent audit log.
export interface Activity {
    id: string;
    company: string;
    description: string;
    created_at: string;
}
