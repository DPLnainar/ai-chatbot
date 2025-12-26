# Conversation Design & Intent Mapping

## Core Intents

### 1. Resume Review & Optimization
**Trigger Keywords**: resume, cv, curriculum vitae, review my resume

**User Needs**:
- Resume formatting and structure feedback
- Content optimization for ATS systems
- Tailoring resume for specific roles/companies
- Highlighting relevant projects and skills
- Action verb suggestions

**Response Pattern**:
- Ask for specific role/company if not provided
- Request current resume or key details
- Provide structured feedback (format, content, impact)
- Suggest specific improvements with examples

---

### 2. Mock Interview Practice
**Trigger Keywords**: interview, mock interview, practice, behavioral questions

**User Needs**:
- Technical interview preparation
- Behavioral question practice
- Company-specific interview prep
- Feedback on answers

**Response Pattern**:
- Clarify interview type (technical/behavioral/case)
- Ask about target company/role
- Conduct structured mock session
- Provide constructive feedback
- Share tips and best practices

---

### 3. Skill Assessment & Learning Path
**Trigger Keywords**: skill, learn, improve, gap, weak, strengthen

**User Needs**:
- Identify skill gaps for target roles
- Personalized learning roadmap
- Resource recommendations
- Progress tracking

**Response Pattern**:
- Assess current skill level
- Identify role requirements
- Create structured learning path
- Recommend resources (courses, projects, books)
- Set milestones

---

### 4. Project Suggestions
**Trigger Keywords**: project, build, portfolio, showcase

**User Needs**:
- Project ideas for portfolio
- Guidance on project complexity
- Technology stack recommendations
- Project presentation tips

**Response Pattern**:
- Understand student's domain and skill level
- Suggest 2-3 relevant projects with varying complexity
- Provide tech stack and implementation guidance
- Advise on documentation and showcase

---

### 5. Company Research
**Trigger Keywords**: company, organization, culture, salary, work-life

**User Needs**:
- Company information and culture
- Interview process insights
- Role-specific guidance
- Salary expectations

**Response Pattern**:
- Provide company overview
- Share interview patterns and rounds
- Discuss work culture and values
- Set realistic expectations

---

### 6. Career Path Guidance
**Trigger Keywords**: career, path, future, confused, which domain

**User Needs**:
- Career direction advice
- Domain exploration
- Long-term planning
- Industry trends

**Response Pattern**:
- Explore interests and strengths
- Explain different career paths
- Discuss market demand and trends
- Help prioritize options

---

### 7. Soft Skills Development
**Trigger Keywords**: communication, leadership, teamwork, presentation

**User Needs**:
- Communication improvement
- Leadership development
- Teamwork and collaboration
- Professional etiquette

**Response Pattern**:
- Identify specific skill to improve
- Provide actionable exercises
- Share scenarios and examples
- Conduct role-play if needed

---

### 8. Technical Domain Deep-Dive
**Domain-Specific Intents**:

#### Software Development
- DSA problem-solving
- System design concepts
- Framework/language-specific questions
- Code review and best practices

#### AI/ML
- Algorithm explanations
- Model selection and tuning
- Project implementation guidance
- Research paper discussions

#### VLSI
- Design flow explanations
- Tool usage guidance
- Verification strategies
- Industry standards

#### Embedded Systems
- Hardware-software integration
- Protocol understanding
- Debugging techniques
- RTOS concepts

#### Mechanical Engineering
- CAD modeling guidance
- Manufacturing processes
- Simulation and analysis
- Quality standards

---

## Conversation Flows

### Flow 1: First-Time User
1. Greeting and introduction
2. Understand student profile (name, major, year)
3. Identify immediate needs
4. Set goals and expectations
5. Provide initial guidance

### Flow 2: Resume Review Session
1. Request resume or key details
2. Ask about target role/company
3. Analyze structure, content, impact
4. Provide specific feedback
5. Suggest improvements
6. Offer follow-up review

### Flow 3: Mock Interview
1. Clarify interview type and role
2. Set context and format
3. Ask questions one by one
4. Listen to answers
5. Provide feedback after each answer
6. Summarize strengths and areas for improvement

### Flow 4: Skill Development Plan
1. Assess current skills
2. Identify target role requirements
3. Find skill gaps
4. Create learning roadmap
5. Recommend resources
6. Set checkpoints for progress

---

## Fallback Strategies

### When Query is Unclear
- Ask clarifying questions
- Provide examples of what you can help with
- Offer suggested topics

### When Information is Insufficient
- Request additional context
- Ask about specific goals
- Narrow down the scope

### When Outside Scope
- Acknowledge the limitation
- Redirect to general career advice
- Suggest external resources

---

## Personalization Hooks

- Student name and preferred address
- Academic major and year
- Target companies and roles
- Completed projects and internships
- Skill level and experience
- Career goals and aspirations
- Previous conversation context

---

## Success Metrics

- User engagement (messages per session)
- Session completion rate
- Positive feedback responses
- Actionable advice provided
- User goal achievement (tracked over time)
