from datetime import datetime, timezone

from agents.calendar import CalendarAgent
from agents.reporter import ReportingAgent


def generate_hologram_briefing(reporter: ReportingAgent, calendar: CalendarAgent) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    briefing = reporter.generate_daily_briefing(date_str)

    lines = []
    lines.append("=" * 60)
    lines.append("  DAILY HOLOGRAM BRIEFING — Rebel Command Report")
    lines.append(f"  {briefing.date}")
    lines.append("")
    lines.append("  General Leia,")
    lines.append("")
    lines.append("  Here is today's Rebel Command briefing.")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total Requests: {briefing.total_messages}")
    lines.append(f"Quarantined (Dark Side threats): {briefing.quarantined}")
    lines.append(f"Encrypted (Yoda strategy): {briefing.encrypted}")
    lines.append("")

    lines.append("By Category:")
    format_by = briefing.by_category
    lines.append(f"  - Calendar bookings:       {format_by.get('calendar_booking', 0)}")
    lines.append(f"  - Planet help:             {format_by.get('planet_help', 0)}")
    lines.append(f"  - Recruitment:             {format_by.get('recruitment', 0)}")
    lines.append(f"  - Soldier support:         {format_by.get('soldier_support', 0)}")
    lines.append(f"  - Population training:     {format_by.get('population_training', 0)}")
    lines.append(f"  - Logistics:               {format_by.get('logistics', 0)}")
    lines.append(f"  - Jedi Training & Diplomacy: {format_by.get('jedi_training_diplomacy', 0)}")
    lines.append(f"  - Ahsoka Special Missions: {format_by.get('ahsoka_special_mission', 0)}")
    lines.append(f"  - Yoda Encrypted Strategy: {format_by.get('yoda_encrypted_strategy', 0)}")
    lines.append(f"  - Security threats:        {format_by.get('urgent_security', 0)}")
    lines.append(f"  - Data support:            {format_by.get('data_support', 0)}")
    lines.append(f"  - Protection missions:     {format_by.get('special_protection', 0)}")
    lines.append(f"  - Field operations:        {format_by.get('field_operations', 0)}")
    lines.append(f"  - Partnerships:            {format_by.get('investor_partner', 0)}")
    lines.append(f"  - Other:                   {format_by.get('other', 0)}")
    lines.append("")

    lines.append("Delegated Missions:")
    format_owner = briefing.by_owner
    lines.append(f"  - Yoda:                        {format_owner.get('Yoda', 0)} encrypted strategic cases")
    lines.append(f"  - Luke + Ben Kenobi:           {format_owner.get('Luke Skywalker + Ben Kenobi', 0)} training/diplomacy")
    lines.append(f"  - Ahsoka Tano:                 {format_owner.get('Ahsoka Tano', 0)} special mission reviews")
    lines.append(f"  - R2-D2:                       {format_owner.get('R2-D2', 0)} data and reporting tasks")
    lines.append(f"  - Han Solo:                    {format_owner.get('Han Solo', 0)} logistics missions")
    lines.append(f"  - Chewbacca:                   {format_owner.get('Chewbacca', 0)} field operations")
    lines.append(f"  - Din Djarin:                  {format_owner.get('Din Djarin', 0)} protection missions")
    lines.append(f"  - Rebel Defense Team:          {format_owner.get('Rebel Defense Team', 0)} planetary aid")
    lines.append(f"  - Rebel Recruitment Team:      {format_owner.get('Rebel Recruitment Team', 0)} recruitment")
    lines.append(f"  - Security Team:               {format_owner.get('Security Team', 0)} security")
    lines.append(f"  - Partnerships Team:           {format_owner.get('Partnerships Team', 0)} partnerships")
    lines.append(f"  - Operations Team:             {format_owner.get('Operations Team', 0)} operations")
    lines.append("")

    if briefing.critical_items:
        lines.append("Critical Items:")
        for item in briefing.critical_items:
            lines.append(f"  [{item['priority'].upper()}] {item['sender']}: {item['category']}")
        lines.append("")

    if briefing.security_items:
        lines.append("Security Risks Detected:")
        for item in briefing.security_items:
            indicators = ", ".join(item["indicators"])
            lines.append(f"  Risk: {item['risk']} | Sender: {item['sender']} | {indicators}")
        lines.append("")

    if briefing.leia_decisions:
        lines.append("Requests Requiring Your Decision:")
        for item in briefing.leia_decisions:
            lines.append(f"  {item['sender']}: {item['category']}")
        lines.append("")

    if briefing.blocked_items:
        lines.append("Blocked or Waiting:")
        for item in briefing.blocked_items:
            lines.append(f"  [{item['status']}] {item['sender']}")
        lines.append("")

    if briefing.recommended_focus:
        lines.append("Recommended Focus for Tomorrow:")
        lines.append(f"  {briefing.recommended_focus}")
        lines.append("")

    public_bookings = calendar.get_public_bookings()
    if public_bookings:
        lines.append("Public Calendar Bookings:")
        for b in public_bookings:
            lines.append(f"  {b.requestor}: {b.subject[:60]} ({b.date} @ {b.time})")
        lines.append("")
        lines.append("  [Private Leia calendar details redacted per security policy]")

    lines.append("=" * 60)
    lines.append("  End of Briefing — May the Force be with us")
    lines.append("=" * 60)
    return "\n".join(lines)
