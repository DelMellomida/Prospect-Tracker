const paths = {
    grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
    people: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M16 3a4 4 0 0 1 0 8 M22 21v-2a4 4 0 0 0-3-3.87 M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
    clock: "M12 8v4l3 2 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0",
    activity: "M3 12h4l3-8 4 16 3-8h4", plus: "M12 5v14 M5 12h14",
    search: "m21 21-4.35-4.35 M19 11a8 8 0 1 1-16 0 8 8 0 0 1 16 0",
    arrow: "M5 12h14 m-5-5 5 5-5 5", chevron: "m9 5 7 7-7 7", close: "m6 6 12 12 M6 18 18 6",
    download: "M12 3v12 m-5-5 5 5 5-5 M5 16v5h14v-5", check: "m5 12 4 4L19 6",
    calendar: "M8 2v4 M16 2v4 M3 10h18 M3 5h18v16H3z", trend: "m3 17 6-6 4 4 8-12 M15 3h6v6",
    mail: "M3 5h18v14H3z m0 0 9 7 9-7", edit: "m16 3 5 5-12 12-6 1 1-6z M14 5l5 5",
    trash: "M3 6h18 M9 6V3h6v3 M5 6l1 15h12l1-15 M10 10v7 M14 10v7",
    leaf: "M20 3C9 2 3 8 6 15s13 5 14-12Z M4 21 16 9",
} as const;
export function Icon({ name, size = 20 }: {
    name: keyof typeof paths;
    size?: number;
}) {
    return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]}/></svg>;
}
