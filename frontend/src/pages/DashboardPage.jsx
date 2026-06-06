import {

    useState,

    useEffect

} from "react";

import MetricCard from "../components/dashboard/MetricCard";

import AuditTable from "../components/dashboard/AuditTable";

import MemoryTable from "../components/dashboard/MemoryTable";

import {

    getAuditEvents,

    getAllMemories,

    getAttackStatistics,

    getAttackSimulator,

    getTimeline,

    getTrustBreakdown,

    getUserRisk,

    getMemoryHistory,

    exportAuditCSV,

    exportMemoryCSV,

    exportHistoryCSV

} from "../api/attacklayer";

import "../styles/dashboard.css";

function DashboardPage(){

    const [

        events,

        setEvents

    ]=useState([]);

    const [

        memories,

        setMemories

    ]=useState([]);

    const [

        simulator,

        setSimulator

    ]=useState({});

    const [

        attackStats,

        setAttackStats

    ]=useState({});

    const [

        userRisk,

        setUserRisk

    ]=useState({});

    const [

        trust,

        setTrust

    ]=useState({});

    const [

        timeline,

        setTimeline

    ]=useState([]);

    const [

        history,

        setHistory

    ]=useState([]);

    useEffect(

        ()=>{

            loadDashboard();

            const timer=

            setInterval(

                loadDashboard,

                3000

            );

            return ()=>

            clearInterval(

                timer

            );

        },

        []

    );

    async function loadDashboard(){

        try{

            const audit=

            await getAuditEvents();

            const memory=

            await getAllMemories();

            const attack=

            await getAttackStatistics();

            const sim=

            await getAttackSimulator();

            const risk=

            await getUserRisk();

            const trustData=

            await getTrustBreakdown();

            const time=

            await getTimeline();

            const memoryHistory=

            await getMemoryHistory();

            setEvents(

                audit

            );

            setMemories(

                memory

            );

            setAttackStats(

                attack

            );

            setSimulator(

                sim

            );

            setUserRisk(

                risk

            );

            setTrust(

                trustData

            );

            setTimeline(

                time

            );

            setHistory(

                memoryHistory

            );

        }

        catch(

            error

        ){

            console.log(

                error

            );

        }

    }

    return(

        <div

            className=

            "dashboard"

        >

            <div

                className=

                "dashboard-title"

            >

                <h1>

                    ATTACKLAYER

                </h1>

                <p>

                    Semantic Security Firewall

                </p>

            </div>

            <div

                className=

                "top-grid"

            >

                <div

                    className=

                    "panel"

                >

                    <h2>

                        USER RISK PROFILE

                    </h2>

                    <div

                        className=

                        "card-grid"

                    >

                        <MetricCard

                            title="Trust"

                            value={

                                userRisk.trust_score

                            }

                        />

                        <MetricCard

                            title="Risk"

                            value={

                                userRisk.risk_level

                            }

                        />

                        <MetricCard

                            title="Blocked"

                            value={

                                userRisk.blocked_requests

                            }

                        />

                        <MetricCard

                            title="Status"

                            value={

                                userRisk.status

                            }

                        />

                    </div>

                </div>

                <div

                    className=

                    "panel"

                >

                    <h2>

                        ATTACK SIMULATOR

                    </h2>

                    <div

                        className=

                        "card-grid"

                    >

                        <MetricCard

                            title="Passwords"

                            value={

                                simulator.password_attacks

                            }

                        />

                        <MetricCard

                            title="Injection"

                            value={

                                simulator.prompt_injections

                            }

                        />

                        <MetricCard

                            title="Secrets"

                            value={

                                simulator.secret_retrievals

                            }

                        />

                        <MetricCard

                            title="Poison"

                            value={

                                simulator.memory_poisoning

                            }

                        />

                    </div>

                </div>

            </div>

            <div

                className=

                "panel"

            >

                <h2>

                    ATTACK ANALYTICS

                </h2>

                <div

                    className=

                    "card-grid"

                >

                    <MetricCard

                        title="General Chat"

                        value={

                            attackStats.general_chat

                        }

                    />

                    <MetricCard

                        title="Reads"

                        value={

                            attackStats.memory_reads

                        }

                    />

                    <MetricCard

                        title="Writes"

                        value={

                            attackStats.memory_writes

                        }

                    />

                    <MetricCard

                        title="Blocked"

                        value={

                            attackStats.blocked

                        }

                    />

                    <MetricCard

                        title="Passwords"

                        value={

                            attackStats.password_attacks

                        }

                    />

                    <MetricCard

                        title="Prompt Injection"

                        value={

                            attackStats.prompt_injections

                        }

                    />

                    <MetricCard

                        title="Secret Retrieval"

                        value={

                            attackStats.secret_retrievals

                        }

                    />

                </div>

            </div>

            <div

                className=

                "panel"

            >

                <h2>

                    LIVE SECURITY EVENTS

                </h2>

                <AuditTable

                    events={

                        events

                    }

                />

            </div>

            <div

                className=

                "bottom-grid"

            >

                <div

                    className=

                    "panel"

                >

                    <h2>

                        MEMORY VAULT

                    </h2>

                    <MemoryTable

                        memories={

                            memories

                        }

                    />

                </div>

                <div

                    className=

                    "panel"

                >

                    <h2>

                        SECURITY TIMELINE

                    </h2>

                    {

                        timeline.map(

                            (

                                item,

                                index

                            )=>

                            (

                                <div

                                    key={

                                        index

                                    }

                                    className=

                                    "timeline-item"

                                >

                                    <div

                                        className=

                                        "timeline-time"

                                    >

                                        {

                                            item.time

                                        }

                                    </div>

                                    <div

                                        className=

                                        "timeline-event"

                                    >

                                        {

                                            item.event

                                        }

                                    </div>

                                    <div

                                        className=

                                        "timeline-message"

                                    >

                                        {

                                            item.message

                                        }

                                    </div>

                                </div>

                            )

                        )

                    }

                </div>

            </div>

            <div

                className=

                "bottom-grid"

            >

                <div

                    className=

                    "panel"

                >

                    <h2>

                        MEMORY HISTORY

                    </h2>

                    {

                        history.length===0

                        ?

                        <p>

                            No history

                        </p>

                        :

                        history.map(

                            (

                                item,

                                index

                            )=>

                            (

                                <div

                                    key={

                                        index

                                    }

                                    className=

                                    "timeline-item"

                                >

                                    <div

                                        className=

                                        "timeline-time"

                                    >

                                        {

                                            item.time

                                        }

                                    </div>

                                    <div

                                        className=

                                        "timeline-event"

                                    >

                                        Version

                                        {

                                            item.old_version

                                        }

                                        →

                                        {

                                            item.new_version

                                        }

                                    </div>

                                    <div

                                        className=

                                        "timeline-message"

                                    >

                                        {

                                            item.old_fact

                                        }

                                    </div>

                                    <div

                                        className=

                                        "timeline-message"

                                    >

                                        ↓

                                    </div>

                                    <div

                                        className=

                                        "timeline-message"

                                    >

                                        {

                                            item.new_fact

                                        }

                                    </div>

                                </div>

                            )

                        )

                    }

                </div>

                <div

    className=

    "panel"

>

    <h2>

        DEVELOPER REPORTS

    </h2>

    <div

        className=

        "report-grid"

    >

        <div

            className=

            "report-card"

            onClick={

                exportAuditCSV

            }

        >

            <div

                className=

                "report-icon"

            >

                📄

            </div>

            <h3>

                AUDIT REPORT

            </h3>

            <p>

                Download CSV

            </p>

        </div>

        <div

            className=

            "report-card"

            onClick={

                exportMemoryCSV

            }

        >

            <div

                className=

                "report-icon"

            >

                🗄️

            </div>

            <h3>

                MEMORY VAULT

            </h3>

            <p>

                Download CSV

            </p>

        </div>

        <div

            className=

            "report-card"

            onClick={

                exportHistoryCSV

            }

        >

            <div

                className=

                "report-icon"

            >

                🕒

            </div>

            <h3>

                MEMORY HISTORY

            </h3>

            <p>

                Download CSV

            </p>

        </div>

    </div>

</div>

            </div>

        </div>

    );

}

export default DashboardPage;