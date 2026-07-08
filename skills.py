"""
skills.py
A normalized skill taxonomy plus per-role requirement definitions. This is
the "ground truth" that the parser checks resume text against, the scorer
uses for the Skills Match component, and the role matcher / JD matcher both
build on. Keeping it in one place means every feature agrees on what
"Python" or "Power BI" means.
"""
from __future__ import annotations

# --------------------------------------------------------------------------- #
# Flat taxonomy: canonical skill name -> set of surface forms to match in text
# Matching is case-insensitive and uses word boundaries (see parser.py).
# --------------------------------------------------------------------------- #
SKILL_TAXONOMY: dict[str, list[str]] = {
    # Programming languages
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C": [r"\bc\b"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "SQL": ["sql"],
    "R": [r"\br\b", "r programming", "r language"],
    "Scala": ["scala"],
    "Go": ["golang", r"\bgo\b"],
    "Ruby": ["ruby"],
    "PHP": ["php"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],

    # Data tooling
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Excel": ["excel", "ms excel", "microsoft excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Looker": ["looker"],
    "SAS": ["sas"],
    "SPSS": ["spss"],

    # Databases
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo"],
    "Oracle DB": ["oracle db", "oracle database"],
    "SQLite": ["sqlite"],
    "Redis": ["redis"],
    "Snowflake": ["snowflake"],
    "BigQuery": ["bigquery", "big query"],

    # ML / AI
    "Machine Learning": ["machine learning", "\\bml\\b"],
    "Deep Learning": ["deep learning"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Keras": ["keras"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "\\bcv\\b"],
    "XGBoost": ["xgboost"],
    "LightGBM": ["lightgbm"],
    "Statistics": ["statistics", "statistical analysis"],

    # Cloud / DevOps
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Jenkins": ["jenkins"],
    "Git": ["git"],
    "GitHub": ["github"],
    "GitLab": ["gitlab"],
    "CI/CD": ["ci/cd", "continuous integration"],
    "Terraform": ["terraform"],

    # Web frameworks
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Vue": ["vue", "vue.js"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Spring Boot": ["spring boot"],

    # Analytics / BI
    "Data Visualization": ["data visualization", "data viz"],
    "A/B Testing": ["a/b testing", "ab testing"],

    # Project management
    "Agile": ["agile"],
    "Scrum": ["scrum"],
    "Jira": ["jira"],
    "Kanban": ["kanban"],
    "Requirements Gathering": ["requirements gathering"],
    "Stakeholder Management": ["stakeholder management"],

    # Core CS fundamentals
    "Data Structures": ["data structures"],
    "Algorithms": ["algorithms"],
    "OOP": ["object-oriented programming", "\\boop\\b"],
    "System Design": ["system design"],
    "Model Deployment": ["model deployment", "mlops"],

    # Soft skills
    "Communication": ["communication"],
    "Leadership": ["leadership"],
    "Teamwork": ["teamwork", "collaboration"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Time Management": ["time management"],
    "Critical Thinking": ["critical thinking"],


    # Frontend
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Next.js": ["next.js", "nextjs"],
    "Redux": ["redux"],
    "Tailwind CSS": ["tailwind", "tailwind css"],

    # Design
    "Figma": ["figma"],
    "Adobe XD": ["adobe xd"],
    "Wireframing": ["wireframing", "wireframes"],
    "Prototyping": ["prototyping", "prototype"],
    "Design Systems": ["design systems", "design system"],
    "User Research": ["user research"],
    "Usability Testing": ["usability testing"],
    "Accessibility": ["accessibility"],

    # Backend
    "API Development": ["api development", "rest api", "restful api"],
    "Database Design": ["database design"],
    "Microservices": ["microservices", "microservice"],
    "Hibernate": ["hibernate"],
    "JUnit": ["junit"],

    # AI / LLM
    "LLMs": ["llm", "llms", "large language model", "large language models"],
    "Prompt Engineering": ["prompt engineering"],
    "LangChain": ["langchain"],
    "RAG": ["rag", "retrieval augmented generation"],
    "Vector Databases": ["vector database", "vector databases"],

    # Data Engineering
    "ETL": ["etl"],
    "Data Warehousing": ["data warehouse", "data warehousing"],
    "Big Data": ["big data"],
    "Spark": ["spark", "apache spark"],
    "Airflow": ["airflow", "apache airflow"],
    "Kafka": ["kafka", "apache kafka"],
    "DAX": ["dax"],
    "Data Modeling": ["data modeling"],

    # DevOps / Cloud
    "Linux": ["linux"],
    "Cloud Computing": ["cloud computing"],
    "Networking": ["networking"],
    "Monitoring": ["monitoring"],
    "Security": ["security"],

    # Cybersecurity
    "Network Security": ["network security"],
    "Risk Assessment": ["risk assessment"],
    "Incident Response": ["incident response"],
    "Security Tools": ["security tools"],
    "SIEM": ["siem"],
    "Penetration Testing": ["penetration testing", "pentesting"],
    "OWASP": ["owasp"],
    "Forensics": ["digital forensics", "forensics"],

    # QA
    "Testing": ["testing"],
    "Test Cases": ["test cases", "test case design"],
    "Automation Testing": ["automation testing"],
    "Bug Tracking": ["bug tracking"],
    "Selenium": ["selenium"],
    "Cypress": ["cypress"],
    "API Testing": ["api testing"],
    "JMeter": ["jmeter"],

    # Product / Project
    "Roadmapping": ["roadmapping", "product roadmap"],
    "Analytics": ["analytics"],
    "Product Strategy": ["product strategy"],
    "Project Planning": ["project planning"],
    "Risk Management": ["risk management"],
    "Budgeting": ["budgeting"],
    "Reporting": ["reporting"],

    # Mobile
    "Mobile Development": ["mobile development"],
    "Android": ["android"],
    "iOS": ["ios"],
    "Flutter": ["flutter"],
    "React Native": ["react native"],
    "Firebase": ["firebase"],
    "API Integration": ["api integration"],

    # Leadership
    "Leadership": ["leadership"],
    "Team Management": ["team management"],
    "Mentoring": ["mentoring", "mentor"],
    "Decision Making": ["decision making"],
    "Conflict Resolution": ["conflict resolution"],
    "Strategic Planning": ["strategic planning"],

    # Communication
    "Public Speaking": ["public speaking"],
    "Presentation Skills": ["presentation skills"],
    "Technical Writing": ["technical writing"],
    "Business Communication": ["business communication"],
    "Negotiation": ["negotiation"],

    # Project Management
    "Project Management": ["project management"],
    "Project Planning": ["project planning"],
    "Resource Management": ["resource management"],
    "Budget Management": ["budget management"],
    "Risk Management": ["risk management"],

    # Sales & Marketing
    "Digital Marketing": ["digital marketing"],
    "SEO": ["seo", "search engine optimization"],
    "SEM": ["sem"],
    "Content Marketing": ["content marketing"],
    "Social Media Marketing": ["social media marketing"],
    "Lead Generation": ["lead generation"],

    # HR & Recruiting
    "Recruitment": ["recruitment"],
    "Talent Acquisition": ["talent acquisition"],
    "Employee Relations": ["employee relations"],
    "Performance Management": ["performance management"],
    "Training & Development": ["training and development"],

    # Finance
    "Financial Analysis": ["financial analysis"],
    "Financial Modeling": ["financial modeling"],
    "Accounting": ["accounting"],
    "Budgeting": ["budgeting"],
    "Forecasting": ["forecasting"],

    # Operations
    "Supply Chain Management": ["supply chain management"],
    "Inventory Management": ["inventory management"],
    "Process Improvement": ["process improvement"],
    "Operations Management": ["operations management"],
    "Lean Six Sigma": ["lean six sigma"],

    # Healthcare
    "Patient Care": ["patient care"],
    "Clinical Research": ["clinical research"],
    "Healthcare Management": ["healthcare management"],
    "Medical Coding": ["medical coding"],

    # Education
    "Teaching": ["teaching"],
    "Curriculum Development": ["curriculum development"],
    "Classroom Management": ["classroom management"],
    "Instructional Design": ["instructional design"],

    # Certifications
    "AWS Certified Solutions Architect": ["aws certified solutions architect"],
    "Google Data Analytics": ["google data analytics"],
    "PMP": ["pmp", "project management professional"],
    "Scrum Master": ["scrum master"],
    "Azure Fundamentals": ["azure fundamentals"],
    "CompTIA Security+": ["comptia security+"],
    "CCNA": ["ccna"],
    "Tableau Desktop Specialist": ["tableau desktop specialist"],

    # Civil Engineering
    "AutoCAD": ["autocad"],
    "Construction Management": ["construction management"],
    "Surveying": ["surveying"],
    "Structural Design": ["structural design"],
    "Revit": ["revit"],
    "STAAD Pro": ["staad pro", "staad"],

    # Mechanical Engineering
    "CAD": ["cad"],
    "SolidWorks": ["solidworks"],
    "Manufacturing": ["manufacturing"],
    "Thermodynamics": ["thermodynamics"],
    "CATIA": ["catia"],
    "ANSYS": ["ansys"],
    "Quality Control": ["quality control"],

    # Electrical Engineering
    "Circuit Design": ["circuit design"],
    "Power Systems": ["power systems"],
    "Electrical Design": ["electrical design"],
    "PLC": ["plc"],
    "SCADA": ["scada"],
    "Safety Compliance": ["safety compliance"],

    # Hospitality
    "Hospitality Management": ["hospitality management"],
    "Customer Service": ["customer service"],
    "Team Management": ["team management"],
    "Guest Relations": ["guest relations"],
    "Food & Beverage Management": ["food and beverage management", "f&b management"],
    "Event Planning": ["event planning"],

    # Finance & Accounting
    "Accounting": ["accounting"],
    "Financial Analysis": ["financial analysis"],
    "Bookkeeping": ["bookkeeping"],
    "Taxation": ["taxation"],
    "Tally": ["tally"],
    "QuickBooks": ["quickbooks"],
    "Auditing": ["auditing"],
    "Financial Modeling": ["financial modeling"],
    "Forecasting": ["forecasting"],

    # Marketing
    "Digital Marketing": ["digital marketing"],
    "SEO": ["seo", "search engine optimization"],
    "Content Marketing": ["content marketing"],
    "Google Ads": ["google ads"],
    "Social Media Marketing": ["social media marketing"],
    "Email Marketing": ["email marketing"],

    # HR
    "Recruitment": ["recruitment"],
    "Talent Acquisition": ["talent acquisition"],
    "Employee Relations": ["employee relations"],
    "Performance Management": ["performance management"],
    "Payroll Management": ["payroll management"],
    "Conflict Resolution": ["conflict resolution"],
    "Training & Development": ["training and development", "training & development"],

    # Education
    "Teaching": ["teaching"],
    "Curriculum Development": ["curriculum development"],
    "Classroom Management": ["classroom management"],
    "Lesson Planning": ["lesson planning"],
    "Mentoring": ["mentoring"],
    "Presentation Skills": ["presentation skills"],

    # Healthcare
    "Patient Care": ["patient care"],
    "Healthcare Management": ["healthcare management"],
    "Clinical Research": ["clinical research"],
    "Medical Coding": ["medical coding"],

    # Design
    "Graphic Design": ["graphic design"],
    "Adobe Photoshop": ["photoshop", "adobe photoshop"],
    "Adobe Illustrator": ["illustrator", "adobe illustrator"],
    "Visual Design": ["visual design"],
    "Creativity": ["creativity"],
    "Branding": ["branding"],
    "UI Design": ["ui design"],

    # Legal
    "Legal Research": ["legal research"],
    "Contract Drafting": ["contract drafting"],
    "Compliance": ["compliance"],
    "Corporate Law": ["corporate law"],
    "Litigation": ["litigation"],
    "Negotiation": ["negotiation"],

    # Supply Chain
    "Supply Chain Management": ["supply chain management"],
    "Inventory Management": ["inventory management"],
    "Procurement": ["procurement"],
    "Logistics Management": ["logistics management"],
    "ERP Systems": ["erp", "erp systems"],

    # Sales
    "Sales Management": ["sales management"],
    "Lead Generation": ["lead generation"],
    "CRM": ["crm", "customer relationship management"],
    "Business Development": ["business development"],
    "Client Management": ["client management"],

    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Next.js": ["next.js", "nextjs"],
    "Redux": ["redux"],
    "Tailwind CSS": ["tailwind", "tailwind css"],

    "API Development": ["api development", "rest api", "restful api"],
    "Database Design": ["database design"],

    "LLMs": ["llm", "llms", "large language model"],
    "Prompt Engineering": ["prompt engineering"],
    "LangChain": ["langchain"],
    "RAG": ["rag", "retrieval augmented generation"],
    "Vector Databases": ["vector database", "vector databases"],

    "ETL": ["etl"],
    "Data Warehousing": ["data warehousing"],
    "Big Data": ["big data"],
    "Spark": ["spark", "apache spark"],
    "Airflow": ["airflow", "apache airflow"],
    "Kafka": ["kafka", "apache kafka"],
}


# --------------------------------------------------------------------------- #
# Role requirement profiles
# --------------------------------------------------------------------------- #
ROLE_REQUIREMENTS: dict[str, dict[str, list[str]]] = {
    "Data Analyst": {
        "required": ["SQL", "Excel", "Python", "Data Visualization", "Statistics"],
        "nice_to_have": ["Power BI", "Tableau", "R", "Pandas", "A/B Testing"],
    },
    "Data Scientist": {
        "required": ["Python", "Machine Learning", "Statistics", "SQL", "Pandas", "Scikit-learn"],
        "nice_to_have": ["Deep Learning", "TensorFlow", "PyTorch", "NLP", "R"],
    },
    "Software Engineer": {
        "required": ["Data Structures", "Algorithms", "Git", "SQL", "OOP"],
        "nice_to_have": ["Docker", "CI/CD", "System Design", "AWS", "Python", "Java"],
    },
    "Machine Learning Engineer": {
        "required": ["Python", "Machine Learning", "Scikit-learn", "SQL", "Model Deployment"],
        "nice_to_have": ["TensorFlow", "PyTorch", "Docker", "Kubernetes", "AWS", "Deep Learning"],
    },
    "Business Analyst": {
        "required": ["SQL", "Excel", "Requirements Gathering", "Data Visualization", "Stakeholder Management"],
        "nice_to_have": ["Power BI", "Tableau", "Agile", "Jira"],
    },
    "Frontend Developer": {
    "required": ["HTML", "CSS", "JavaScript", "React", "Git"],
    "nice_to_have": ["TypeScript", "Next.js", "Redux", "Tailwind CSS", "Figma"],
    },

    "Backend Developer": {
    "required": ["Python", "SQL", "API Development", "Git", "Database Design"],
    "nice_to_have": ["Django", "Flask", "Docker", "AWS", "Redis"],
    },

    "Full Stack Developer": {
    "required": ["HTML", "CSS", "JavaScript", "React", "SQL"],
    "nice_to_have": ["Node.js", "Docker", "AWS", "MongoDB", "TypeScript"],
    },

    "DevOps Engineer": {
    "required": ["Linux", "Docker", "CI/CD", "Git", "Cloud Computing"],
    "nice_to_have": ["Kubernetes", "AWS", "Terraform", "Jenkins", "Monitoring"],
    },

    "Cloud Engineer": {
    "required": ["AWS", "Cloud Computing", "Networking", "Linux", "Security"],
    "nice_to_have": ["Azure", "GCP", "Terraform", "Docker", "Kubernetes"],
    },

    "Cybersecurity Analyst": {
    "required": ["Network Security", "Risk Assessment", "Incident Response", "Linux", "Security Tools"],
    "nice_to_have": ["SIEM", "Penetration Testing", "Python", "OWASP", "Forensics"],
    },

    "Python Developer": {
    "required": ["Python", "SQL", "Git", "OOP", "API Development"],
    "nice_to_have": ["Django", "Flask", "Docker", "AWS", "Testing"],
    },

    "Java Developer": {
    "required": ["Java", "OOP", "SQL", "Git", "Spring Boot"],
    "nice_to_have": ["Hibernate", "Microservices", "Docker", "AWS", "JUnit"],
    },

    "AI Engineer": {
    "required": ["Python", "Machine Learning", "Deep Learning", "LLMs", "Prompt Engineering"],
    "nice_to_have": ["LangChain", "Vector Databases", "RAG", "PyTorch", "TensorFlow"],
    },

    "Data Engineer": {
    "required": ["SQL", "Python", "ETL", "Data Warehousing", "Big Data"],
    "nice_to_have": ["Spark", "Airflow", "Kafka", "AWS", "Snowflake"],
    },

    "Business Intelligence Developer": {
    "required": ["SQL", "Power BI", "Data Modeling", "Excel", "Data Visualization"],
    "nice_to_have": ["Tableau", "DAX", "Python", "ETL", "Azure"],
    },

    "QA Engineer": {
    "required": ["Testing", "Bug Tracking", "Test Cases", "Automation Testing", "Git"],
    "nice_to_have": ["Selenium", "Cypress", "API Testing", "JMeter", "CI/CD"],
    },

    "UI/UX Designer": {
    "required": ["Figma", "Wireframing", "User Research", "Prototyping", "Design Systems"],
    "nice_to_have": ["Adobe XD", "Usability Testing", "HTML", "CSS", "Accessibility"],
    },

    "Product Manager": {
    "required": ["Roadmapping", "Stakeholder Management", "Agile", "Requirements Gathering", "Analytics"],
    "nice_to_have": ["Jira", "SQL", "A/B Testing", "User Research", "Product Strategy"],
    },

    "Project Manager": {
    "required": ["Project Planning", "Risk Management", "Agile", "Stakeholder Management", "Communication"],
    "nice_to_have": ["Jira", "Scrum", "Budgeting", "Leadership", "Reporting"],
    },

    "Mobile App Developer": {
    "required": ["Mobile Development", "Android", "iOS", "Git", "API Integration"],
    "nice_to_have": ["Flutter", "React Native", "Firebase", "Kotlin", "Swift"],
    },

    "Civil Engineer": {
    "required": ["AutoCAD", "Construction Management", "Surveying", "Structural Design", "Project Planning"],
    "nice_to_have": ["Revit", "STAAD Pro", "Leadership", "Risk Management", "Communication"],
    },

    "Mechanical Engineer": {
        "required": ["CAD", "SolidWorks", "Manufacturing", "Thermodynamics", "Problem Solving"],
        "nice_to_have": ["CATIA", "ANSYS", "Project Management", "Leadership", "Quality Control"],
    },

    "Electrical Engineer": {
        "required": ["Circuit Design", "Power Systems", "Electrical Design", "PLC", "Problem Solving"],
        "nice_to_have": ["SCADA", "AutoCAD", "Project Management", "Leadership", "Safety Compliance"],
    },

    "Hotel Manager": {
        "required": ["Hospitality Management", "Customer Service", "Team Management", "Communication", "Guest Relations"],
        "nice_to_have": ["Event Planning", "Budgeting", "Leadership", "Food & Beverage Management", "Problem Solving"],
    },

    "Restaurant Manager": {
        "required": ["Customer Service", "Team Management", "Food & Beverage Management", "Communication", "Leadership"],
        "nice_to_have": ["Inventory Management", "Budgeting", "Event Planning", "Problem Solving", "Guest Relations"],
    },

    "Accountant": {
        "required": ["Accounting", "Excel", "Financial Analysis", "Bookkeeping", "Taxation"],
        "nice_to_have": ["Tally", "QuickBooks", "Auditing", "Financial Modeling", "Reporting"],
    },

    "Financial Analyst": {
        "required": ["Financial Analysis", "Excel", "Financial Modeling", "Reporting", "Problem Solving"],
        "nice_to_have": ["Power BI", "SQL", "Statistics", "Communication", "Forecasting"],
    },

    "Digital Marketing Specialist": {
        "required": ["Digital Marketing", "SEO", "Content Marketing", "Analytics", "Communication"],
        "nice_to_have": ["Google Ads", "Social Media Marketing", "Email Marketing", "A/B Testing", "Leadership"],
    },

    "HR Manager": {
        "required": ["Recruitment", "Talent Acquisition", "Employee Relations", "Communication", "Leadership"],
        "nice_to_have": ["Performance Management", "Payroll Management", "Conflict Resolution", "Training & Development", "Reporting"],
    },

    "Teacher": {
        "required": ["Teaching", "Curriculum Development", "Classroom Management", "Communication", "Lesson Planning"],
        "nice_to_have": ["Leadership", "Mentoring", "Presentation Skills", "Critical Thinking", "Teamwork"],
    },

    "Nurse": {
        "required": ["Patient Care", "Healthcare Management", "Communication", "Teamwork", "Critical Thinking"],
        "nice_to_have": ["Clinical Research", "Leadership", "Medical Coding", "Problem Solving", "Time Management"],
    },

    "Graphic Designer": {
        "required": ["Graphic Design", "Adobe Photoshop", "Adobe Illustrator", "Visual Design", "Creativity"],
        "nice_to_have": ["Figma", "Branding", "UI Design", "Communication", "Adobe XD"],
    },

    "Lawyer": {
        "required": ["Legal Research", "Contract Drafting", "Compliance", "Communication", "Critical Thinking"],
        "nice_to_have": ["Corporate Law", "Litigation", "Negotiation", "Leadership", "Problem Solving"],
    },

    "Supply Chain Manager": {
        "required": ["Supply Chain Management", "Inventory Management", "Procurement", "Logistics Management", "Communication"],
        "nice_to_have": ["Leadership", "Analytics", "ERP Systems", "Risk Management", "Reporting"],
    },

    "Sales Manager": {
        "required": ["Sales Management", "Lead Generation", "CRM", "Communication", "Business Development"],
        "nice_to_have": ["Negotiation", "Leadership", "Client Management", "Analytics", "Presentation Skills"],
    },
}

SUPPORTED_ROLES = list(ROLE_REQUIREMENTS.keys())


def match_skills_to_role(found_skills: set[str], role: str) -> dict:
    """Compares a resume's detected skill set against a role profile.
    Required skills are weighted more heavily than nice-to-have ones."""
    profile = ROLE_REQUIREMENTS.get(role)
    if not profile:
        return {"match_percent": 0, "missing_skills": [], "strengths": [], "recommendations": []}

    required = profile["required"]
    nice = profile["nice_to_have"]

    required_hit = [s for s in required if s in found_skills]
    nice_hit = [s for s in nice if s in found_skills]
    missing_required = [s for s in required if s not in found_skills]
    missing_nice = [s for s in nice if s not in found_skills]

    # Required skills worth 75% of the match score, nice-to-have 25%
    required_score = (len(required_hit) / len(required)) * 75 if required else 0
    nice_score = (len(nice_hit) / len(nice)) * 25 if nice else 0
    match_percent = round(required_score + nice_score, 1)

    recommendations = []
    if missing_required:
        recommendations.append(f"Add evidence of {', '.join(missing_required[:3])} - these are core requirements for {role}.")
    if missing_nice:
        recommendations.append(f"Consider highlighting {', '.join(missing_nice[:3])} if you have any experience with them.")
    if not missing_required and not missing_nice:
        recommendations.append(f"Your skill set already covers the standard {role} profile well.")

    return {
        "match_percent": match_percent,
        "missing_skills": missing_required + missing_nice,
        "missing_required": missing_required,
        "missing_nice_to_have": missing_nice,
        "strengths": required_hit + nice_hit,
        "recommendations": recommendations,
    }
