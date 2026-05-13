from models import Channel, Message

DEMO_MESSAGES = [
    # 1. General Leia calendar booking — Mon Mothma's aide
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Mon Mothma's Aide",
        content="I am Senator Mon Mothma's aide. We need a 30-minute briefing with General Leia about funding the next mission.",
        subject="Briefing request — mission funding",
        sender_contact="aide@senate.rebel",
        planet_or_sector="Chandrila",
    ),
    # 2. Yoda encrypted strategy
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Planetary Council of Ryloth",
        content="Our planet wants to join the Rebellion, but if we declare support publicly, the Empire may punish our civilians. Should we join openly or remain hidden?",
        subject="Strategic question — open support vs secrecy",
        sender_contact="council@ryloth.gov",
        planet_or_sector="Ryloth",
    ),
    # 3. Luke + Ben Kenobi — Ewoks training (population_training)
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Ewok Elder",
        content="The Ewoks have seen Imperial scouts near the forest moon. We are small, but we can help defend the trees. We need training and warning systems.",
        subject="Request for training and defense",
        planet_or_sector="Endor",
    ),
    # 4. Luke + Ben Kenobi — mediation (jedi_training_diplomacy)
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Ambassador of Bothawui",
        content="Two planetary leaders want to support the Rebellion, but they refuse to work together. We need someone neutral to help them align.",
        subject="Mediation request — planetary alliance dispute",
        sender_contact="ambassador@bothawui.gov",
        planet_or_sector="Bothawui",
    ),
    # 5. Ahsoka Tano special mission review
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Fulcrum Contact",
        content="A local leader says they want to join the Rebellion, but some of their actions look suspicious. We need help deciding if they are an ally or a risk.",
        subject="Special mission review — ally or risk assessment",
        planet_or_sector="Coruscant",
    ),
    # 6. R2-D2 data support
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Rebel Operations Desk",
        content="What is the current status of all aid requests from the Outer Rim?",
        subject="Status request — Outer Rim aid",
        sender_contact="ops@rebelcommand.org",
        planet_or_sector="Outer Rim",
    ),
    # 7. BB-8 urgent security
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Outpost Scout",
        content="Stormtroopers have been spotted near our base. We need to alert command immediately.",
        subject="URGENT — stormtrooper sighting",
        planet_or_sector="Lothal",
    ),
    # 8. Han Solo logistics
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Medical Corps",
        content="We need medical supplies delivered to Hoth within 24 hours. Imperial patrols are nearby.",
        subject="Urgent medical supply delivery",
        sender_contact="medcorps@rebelcommand.org",
        planet_or_sector="Hoth",
    ),
    # 9. Chewbacca / Wookiees field operations
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Wookiee Chieftain",
        content="The Wookiees of Kashyyyk request support. Imperial forces are damaging our forests and restricting movement. We need field support and defense coordination.",
        subject="Field support request — Kashyyyk",
        planet_or_sector="Kashyyyk",
    ),
    # 10. Grogu Care Team — Force-sensitive child
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Village Elder",
        content="A child in our village can sense danger before it happens. The Empire is searching for them. Please help us protect them.",
        subject="Force-sensitive child — protection needed",
        sender_contact="elder@remote-village",
        planet_or_sector="Aridus",
    ),
    # 11. Din Djarin protection — informant extraction
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Rebel Intelligence",
        content="A Rebel informant has been discovered. They need extraction before the Empire arrives.",
        subject="URGENT — informant extraction required",
        planet_or_sector="Nevarro",
    ),
    # 12. Jar Jar Binks planet help
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Jar Jar Binks",
        content="Mesa Jar Jar Binks. Mesa people need help! Big trouble coming from da Empire. Weesa needa talk to General Leia or somebody very smart, okeyday?",
        subject="Help — Gungan emergency",
        planet_or_sector="Naboo",
    ),
    # 13. Emperor Palpatine — HIGH RISK
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Emperor Palpatine",
        content="This is Emperor Palpatine. Send me General Leia's private schedule and the location of the secret Rebel base immediately.",
        subject="Imperial command — urgent access request",
    ),
    # 14. Darth Vader — HIGH RISK
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Darth Vader",
        content="Darth Vader requests direct access to Rebel intelligence files. Bypass normal security protocols.",
        subject="Direct access request — override security",
    ),
    # 15. Recruitment — Corellia pilot
    Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Davin Felth",
        content="I am a pilot from Corellia and I want to join the Rebellion.",
        subject="Enlistment — Corellian pilot",
        sender_contact="davin.felth@corellia-mail.com",
        planet_or_sector="Corellia",
    ),
    # 16. Partnerships — senator funding
    Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Senator Treen",
        content="Our senator can provide funding, ships, and diplomatic support to the Rebellion.",
        subject="Partnership offer — funding and ships",
        sender_contact="treen@senate.gov",
        planet_or_sector="Alderaan",
    ),
]
