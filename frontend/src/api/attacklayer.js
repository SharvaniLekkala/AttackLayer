import axios from "axios";

const API = axios.create({

    baseURL:"http://localhost:8000"

});

export async function sendChatMessage(

    userId,

    message

){

    const response=

    await API.post(

        "/chat/",

        null,

        {

            params:{

                user_id:userId,

                message:message

            }

        }

    );

    return response.data;

}

export async function getAuditEvents(){

    const response=

    await API.get(

        "/audit/events"

    );

    return response.data;

}

export async function getAllMemories(){

    const response=

    await API.get(

        "/memory/all"

    );

    return response.data;

}

export async function getBlockedEvents(){

    const response=

    await API.get(

        "/audit/blocked"

    );

    return response.data;

}

export async function getThreatEvents(){

    const response=

    await API.get(

        "/audit/threats"

    );

    return response.data;

}

export async function getConflictEvents(){

    const response=

    await API.get(

        "/audit/conflicts"

    );

    return response.data;

}

export async function getTrustAnalytics(){

    const response=

    await API.get(

        "/audit/trust"

    );

    return response.data;

}

export async function getAttackStatistics(){

    const response=

    await API.get(

        "/audit/attack-statistics"

    );

    return response.data;

}

export async function getAttackSimulator(){

    const response=

    await API.get(

        "/audit/attack-simulator"

    );

    return response.data;

}

export async function getTimeline(){

    const response=

    await API.get(

        "/audit/timeline"

    );

    return response.data;

}

export async function getTrustBreakdown(){

    const response=

    await API.get(

        "/audit/trust-breakdown"

    );

    return response.data;

}

export async function getUserRisk(){

    const response=

    await API.get(

        "/audit/user-risk"

    );

    return response.data;

}

export async function getMemoryHistory(){

    const response=

    await API.get(

        "/memory/history"

    );

    return response.data;

}

export function exportAuditCSV(){

    window.open(

        "http://localhost:8000/export/audit-csv",

        "_blank"

    );

}

export function exportMemoryCSV(){

    window.open(

        "http://localhost:8000/export/memory-csv",

        "_blank"

    );

}

export function exportHistoryCSV(){

    window.open(

        "http://localhost:8000/export/history-csv",

        "_blank"

    );

}