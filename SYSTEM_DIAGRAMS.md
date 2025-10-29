# Kali AI Command Chaining System - System Diagrams

This document contains visual representations of the system architecture, workflows, and data flows.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface<br/>Rich Formatting]
        Display[Display Manager]
        Prompts[Prompt Manager]
    end
    
    subgraph "Core Agent Layer"
        Agent[AI Agent Core<br/>Orchestration]
        Decision[Decision Engine<br/>Command Selection]
        State[State Manager<br/>Context & History]
    end
    
    subgraph "LLM Integration Layer"
        LLMClient[Ollama Client]
        PromptEngine[Prompt Templates]
        Context[Context Manager]
    end
    
    subgraph "Execution Layer"
        Executor[Command Executor<br/>Subprocess Management]
        Parser[Output Parser<br/>Tool-Specific]
        Interpreter[Result Interpreter<br/>Semantic Analysis]
    end
    
    subgraph "Safety Layer"
        Classifier[Command Classifier]
        Validator[Safety Validator]
        Rules[Safety Rules<br/>Blacklist/Whitelist]
    end
    
    subgraph "Tool Integration Layer"
        Recon[Reconnaissance Tools]
        Vuln[Vulnerability Scanners]
        Exploit[Exploitation Frameworks]
        WebApp[Web Application Testing]
        Wireless[Wireless Security]
        Password[Password Cracking]
        Forensics[Forensics Tools]
        Defense[Defensive Security]
    end
    
    subgraph "Feedback Layer"
        Assessor[Objective Assessor]
        Strategy[Strategy Adjuster]
    end
    
    User[User] --> CLI
    CLI --> Agent
    Agent --> Decision
    Agent --> State
    Agent --> LLMClient
    
    LLMClient --> PromptEngine
    LLMClient --> Context
    LLMClient --> Ollama[Ollama Server<br/>dolphin3-abliterated:8b]
    
    Decision --> Executor
    Executor --> Classifier
    Classifier --> Validator
    Validator --> Rules
    
    Executor --> Parser
    Parser --> Interpreter
    Interpreter --> State
    
    Executor --> Recon
    Executor --> Vuln
    Executor --> Exploit
    Executor --> WebApp
    Executor --> Wireless
    Executor --> Password
    Executor --> Forensics
    Executor --> Defense
    
    Interpreter --> Assessor
    Assessor --> Strategy
    Strategy --> Agent
    
    State --> Display
    Display --> CLI
```

## Command Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Agent
    participant LLM
    participant Safety
    participant Executor
    participant Parser
    participant State
    
    User->>CLI: Provide Security Objective
    CLI->>Agent: Initialize with Objective
    
    loop Until Objective Complete
        Agent->>State: Get Current Context
        State-->>Agent: Context Data
        
        Agent->>LLM: Request Next Command
        Note over LLM: Analyze context<br/>Generate command<br/>Provide reasoning
        LLM-->>Agent: Command + Reasoning
        
        Agent->>Safety: Validate Command
        Safety->>Safety: Classify Risk Level
        
        alt High Risk Command
            Safety->>CLI: Request User Approval
            CLI->>User: Display Command & Risk
            User-->>CLI: Approve/Reject
            CLI-->>Safety: User Decision
        end
        
        alt Command Approved
            Safety-->>Agent: Validation Passed
            Agent->>Executor: Execute Command
            
            Executor->>Executor: Run Subprocess
            Note over Executor: Monitor execution<br/>Capture output<br/>Handle errors
            
            Executor-->>Parser: Raw Output
            Parser->>Parser: Parse Tool Output
            Parser-->>Agent: Structured Data
            
            Agent->>State: Update Context
            State->>State: Add to History<br/>Update Discoveries
            
            Agent->>CLI: Display Results
            CLI->>User: Show Output & Findings
        else Command Rejected
            Safety-->>Agent: Validation Failed
            Agent->>CLI: Display Rejection
        end
        
        Agent->>Agent: Assess Progress
        
        alt Strategy Adjustment Needed
            Agent->>LLM: Request Strategy Change
            LLM-->>Agent: New Strategy
        end
    end
    
    Agent->>CLI: Objective Complete
    CLI->>User: Display Final Report
```

## Safety Validation Flow

```mermaid
flowchart TD
    Start[Command Generated] --> Classify[Classify Command]
    
    Classify --> CheckType{Command Type?}
    
    CheckType -->|Reconnaissance| Safe[Safe Category]
    CheckType -->|Exploitation| HighRisk[High Risk Category]
    CheckType -->|System Modification| HighRisk
    CheckType -->|Password Cracking| HighRisk
    
    Safe --> AutoExecute[Auto-Execute]
    
    HighRisk --> CheckBlacklist{In Blacklist?}
    CheckBlacklist -->|Yes| Block[Block Execution]
    CheckBlacklist -->|No| RequestApproval[Request User Approval]
    
    RequestApproval --> UserDecision{User Approves?}
    UserDecision -->|Yes| LogApproval[Log Approval]
    UserDecision -->|No| Block
    
    LogApproval --> ValidateParams[Validate Parameters]
    ValidateParams --> CheckScope{Within Scope?}
    
    CheckScope -->|Yes| Execute[Execute Command]
    CheckScope -->|No| Block
    
    AutoExecute --> ValidateParams
    
    Execute --> Monitor[Monitor Execution]
    Monitor --> Complete[Execution Complete]
    
    Block --> LogRejection[Log Rejection]
    LogRejection --> End[Return Error]
    
    Complete --> End2[Return Result]
```

## AI Decision Making Process

```mermaid
flowchart TD
    Start[Current State] --> Analyze[Analyze Context]
    
    Analyze --> CheckProgress{Objective<br/>Progress?}
    
    CheckProgress -->|0-25%| Recon[Reconnaissance Phase]
    CheckProgress -->|25-50%| Scan[Scanning Phase]
    CheckProgress -->|50-75%| Exploit[Exploitation Phase]
    CheckProgress -->|75-100%| Report[Reporting Phase]
    
    Recon --> GenOptions1[Generate Command Options]
    Scan --> GenOptions2[Generate Command Options]
    Exploit --> GenOptions3[Generate Command Options]
    Report --> GenOptions4[Generate Command Options]
    
    GenOptions1 --> Rank[Rank Options]
    GenOptions2 --> Rank
    GenOptions3 --> Rank
    GenOptions4 --> Rank
    
    Rank --> Consider{Consider Factors}
    
    Consider --> Factor1[Previous Results]
    Consider --> Factor2[Discovered Info]
    Consider --> Factor3[Tool Availability]
    Consider --> Factor4[Risk Level]
    Consider --> Factor5[Expected Outcome]
    
    Factor1 --> Score[Calculate Scores]
    Factor2 --> Score
    Factor3 --> Score
    Factor4 --> Score
    Factor5 --> Score
    
    Score --> Select[Select Best Option]
    Select --> Validate[Validate Selection]
    
    Validate --> CheckValid{Valid?}
    CheckValid -->|Yes| Return[Return Command]
    CheckValid -->|No| Rank
    
    Return --> End[Execute Command]
```

## State Management Flow

```mermaid
flowchart LR
    subgraph "State Components"
        Objective[Security Objective]
        History[Command History]
        Discoveries[Discoveries]
        Context[Context Window]
        Progress[Progress Metrics]
    end
    
    subgraph "State Operations"
        Add[Add Command]
        Update[Update Discoveries]
        Compress[Compress Context]
        Calculate[Calculate Progress]
        Save[Save Session]
        Load[Load Session]
    end
    
    subgraph "State Outputs"
        FullContext[Full Context for LLM]
        Report[Session Report]
        Export[Export Data]
    end
    
    Objective --> FullContext
    History --> Add
    Add --> Update
    Update --> Discoveries
    Discoveries --> FullContext
    
    History --> Compress
    Compress --> Context
    Context --> FullContext
    
    Discoveries --> Calculate
    Calculate --> Progress
    Progress --> FullContext
    
    History --> Save
    Discoveries --> Save
    Progress --> Save
    
    Save --> SessionFile[(Session File)]
    SessionFile --> Load
    
    History --> Report
    Discoveries --> Report
    Progress --> Report
    
    Report --> Export
```

## Tool Integration Architecture

```mermaid
graph TB
    subgraph "Base Tool Interface"
        BaseTool[Base Tool Class]
        Execute[execute method]
        Parse[parse method]
        Validate[validate method]
    end
    
    subgraph "Reconnaissance Tools"
        Nmap[Nmap Tool]
        Masscan[Masscan Tool]
        DNSEnum[DNS Enum Tool]
    end
    
    subgraph "Vulnerability Tools"
        OpenVAS[OpenVAS Tool]
        Nikto[Nikto Tool]
        ZAP[OWASP ZAP Tool]
    end
    
    subgraph "Exploitation Tools"
        MSF[Metasploit Tool]
        ExploitDB[Exploit-DB Tool]
        SearchSploit[SearchSploit Tool]
    end
    
    subgraph "Web Testing Tools"
        SQLMap[SQLMap Tool]
        Burp[Burp Suite Tool]
        XSSer[XSSer Tool]
    end
    
    BaseTool --> Execute
    BaseTool --> Parse
    BaseTool --> Validate
    
    BaseTool -.inherits.-> Nmap
    BaseTool -.inherits.-> Masscan
    BaseTool -.inherits.-> DNSEnum
    BaseTool -.inherits.-> OpenVAS
    BaseTool -.inherits.-> Nikto
    BaseTool -.inherits.-> ZAP
    BaseTool -.inherits.-> MSF
    BaseTool -.inherits.-> ExploitDB
    BaseTool -.inherits.-> SearchSploit
    BaseTool -.inherits.-> SQLMap
    BaseTool -.inherits.-> Burp
    BaseTool -.inherits.-> XSSer
    
    Executor[Command Executor] --> BaseTool
```

## Context Window Management

```mermaid
flowchart TD
    Start[New Command Executed] --> Add[Add to History]
    
    Add --> CheckSize{History Size > Max?}
    
    CheckSize -->|No| UpdateWindow[Update Context Window]
    CheckSize -->|Yes| Compress[Compress Old Entries]
    
    Compress --> Summarize[Summarize Commands]
    Summarize --> KeepRecent[Keep Recent Full Entries]
    KeepRecent --> UpdateWindow
    
    UpdateWindow --> BuildContext[Build LLM Context]
    
    BuildContext --> Include1[Include Objective]
    BuildContext --> Include2[Include Recent Commands]
    BuildContext --> Include3[Include Discoveries]
    BuildContext --> Include4[Include Progress]
    
    Include1 --> Format[Format for LLM]
    Include2 --> Format
    Include3 --> Format
    Include4 --> Format
    
    Format --> Send[Send to LLM]
    Send --> End[Receive Next Command]
```

## Feedback Loop and Strategy Adjustment

```mermaid
flowchart TD
    Start[Command Executed] --> Analyze[Analyze Result]
    
    Analyze --> CheckSuccess{Successful?}
    
    CheckSuccess -->|Yes| ExtractInfo[Extract Information]
    CheckSuccess -->|No| AnalyzeError[Analyze Error]
    
    ExtractInfo --> UpdateDiscoveries[Update Discoveries]
    UpdateDiscoveries --> AssessProgress[Assess Progress]
    
    AnalyzeError --> ClassifyError{Error Type?}
    
    ClassifyError -->|Timeout| AdjustTiming[Adjust Timing Parameters]
    ClassifyError -->|Permission| SuggestEscalation[Suggest Privilege Escalation]
    ClassifyError -->|Not Found| TryAlternative[Try Alternative Tool]
    ClassifyError -->|Network| CheckConnectivity[Check Target Connectivity]
    
    AdjustTiming --> Retry[Retry Command]
    SuggestEscalation --> NewStrategy
    TryAlternative --> NewStrategy
    CheckConnectivity --> NewStrategy
    
    AssessProgress --> CheckObjective{Objective<br/>Achieved?}
    
    CheckObjective -->|Yes| Complete[Mark Complete]
    CheckObjective -->|No| CheckStuck{Making<br/>Progress?}
    
    CheckStuck -->|Yes| Continue[Continue Current Strategy]
    CheckStuck -->|No| DetectPattern[Detect Failure Pattern]
    
    DetectPattern --> NewStrategy[Request Strategy Adjustment]
    
    NewStrategy --> QueryLLM[Query LLM for New Approach]
    QueryLLM --> UpdateGoals[Update Goals]
    UpdateGoals --> Continue
    
    Continue --> NextCommand[Generate Next Command]
    Retry --> NextCommand
    Complete --> End[Generate Report]
```

## Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initializing: User provides objective
    
    Initializing --> Planning: Parse objective
    Planning --> Planning: Create goals
    Planning --> Executing: Goals defined
    
    Executing --> Executing: Execute command
    Executing --> Analyzing: Command complete
    
    Analyzing --> Analyzing: Parse output
    Analyzing --> Executing: Next command
    Analyzing --> Adjusting: Strategy change needed
    
    Adjusting --> Planning: Replan approach
    Adjusting --> Executing: Continue with adjustment
    
    Executing --> Paused: User interruption
    Paused --> Executing: Resume session
    Paused --> [*]: User terminates
    
    Analyzing --> Completed: Objective achieved
    Analyzing --> Failed: Unrecoverable error
    
    Completed --> [*]: Generate report
    Failed --> [*]: Generate error report
```

## Data Flow Through System

```mermaid
flowchart LR
    subgraph Input
        UserObj[User Objective]
        Config[Configuration]
    end
    
    subgraph Processing
        Parse[Parse & Plan]
        Generate[Generate Command]
        Execute[Execute Command]
        ParseOut[Parse Output]
        Interpret[Interpret Results]
    end
    
    subgraph Storage
        State[State Manager]
        History[Command History]
        Disc[Discoveries]
    end
    
    subgraph Output
        Display[CLI Display]
        Logs[Log Files]
        Report[Final Report]
    end
    
    UserObj --> Parse
    Config --> Parse
    Parse --> Generate
    
    Generate --> Execute
    Execute --> ParseOut
    ParseOut --> Interpret
    
    Interpret --> State
    State --> History
    State --> Disc
    
    State --> Generate
    State --> Display
    History --> Logs
    Disc --> Report
    
    Display --> User[User]
    Report --> User
```

## Error Handling Flow

```mermaid
flowchart TD
    Error[Error Detected] --> Classify{Error Category}
    
    Classify -->|Execution Error| ExecError[Command Execution Error]
    Classify -->|Network Error| NetError[Network Error]
    Classify -->|LLM Error| LLMError[LLM Communication Error]
    Classify -->|Parse Error| ParseError[Output Parsing Error]
    
    ExecError --> CheckRetry1{Retryable?}
    NetError --> CheckRetry2{Retryable?}
    LLMError --> CheckRetry3{Retryable?}
    ParseError --> CheckRetry4{Retryable?}
    
    CheckRetry1 -->|Yes| Retry1[Retry with Backoff]
    CheckRetry1 -->|No| Log1[Log Error]
    
    CheckRetry2 -->|Yes| Retry2[Retry with Backoff]
    CheckRetry2 -->|No| Log2[Log Error]
    
    CheckRetry3 -->|Yes| Retry3[Retry with Backoff]
    CheckRetry3 -->|No| Log3[Log Error]
    
    CheckRetry4 -->|Yes| UseGeneric[Use Generic Parser]
    CheckRetry4 -->|No| Log4[Log Error]
    
    Retry1 --> Success1{Success?}
    Retry2 --> Success2{Success?}
    Retry3 --> Success3{Success?}
    UseGeneric --> Success4{Success?}
    
    Success1 -->|Yes| Continue[Continue Execution]
    Success1 -->|No| Log1
    
    Success2 -->|Yes| Continue
    Success2 -->|No| Log2
    
    Success3 -->|Yes| Continue
    Success3 -->|No| Log3
    
    Success4 -->|Yes| Continue
    Success4 -->|No| Log4
    
    Log1 --> Notify[Notify User]
    Log2 --> Notify
    Log3 --> Notify
    Log4 --> Notify
    
    Notify --> Alternative[Suggest Alternative]
    Alternative --> Continue
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Kali Linux System"
        subgraph "Application Layer"
            CLI[CLI Application]
            Agent[AI Agent]
            Tools[Kali Tools]
        end
        
        subgraph "Data Layer"
            Config[config.yaml]
            Logs[Log Files]
            Sessions[Session Data]
        end
    end
    
    subgraph "LLM Infrastructure"
        Local[Local Ollama]
        Remote[Remote Ollama Server]
    end
    
    subgraph "Target Environment"
        Targets[Target Systems]
        Network[Target Network]
    end
    
    CLI --> Agent
    Agent --> Config
    Agent --> Logs
    Agent --> Sessions
    
    Agent --> Local
    Agent --> Remote
    
    Agent --> Tools
    Tools --> Targets
    Tools --> Network
    
    Local -.model.-> Model[dolphin3-abliterated:8b]
    Remote -.model.-> Model
```

---

These diagrams provide a comprehensive visual understanding of the system's architecture, workflows, and data flows. They can be used for:

- System design discussions
- Implementation guidance
- Documentation
- Training materials
- Troubleshooting
- Architecture reviews