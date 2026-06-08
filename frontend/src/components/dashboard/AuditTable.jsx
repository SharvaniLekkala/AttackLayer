function AuditTable({

    events

}){

    function getDecisionColor(

        decision

    ){

        if(

            decision===

            "BLOCK"

        ){

            return "#ef4444";

        }

        if(

            decision===

            "REVIEW"

            ||

            decision===

            "ALLOW_WITH_WARNING"

        ){

            return "#f59e0b";

        }

        return "#22c55e";

    }

    function getThreatColor(

        threat

    ){

        if(

            threat===

            "NONE"

        ){

            return "#22c55e";

        }

        return "#ef4444";

    }

    return(

        <table

            className=

            "dashboard-table"

        >

            <thead>

                <tr>

                    <th>

                        Time

                    </th>

                    <th>

                        Prompt

                    </th>

                    <th>

                        Operation

                    </th>

                    <th>

                        Threat

                    </th>

                    <th>

                        Risk

                    </th>

                    <th>

                        Decision

                    </th>

                </tr>

            </thead>

            <tbody>

                {

                    events.length===0

                    ?

                    <tr>

                        <td

                            colSpan="6"

                        >

                            No activity

                        </td>

                    </tr>

                    :

                    events.map(

                        (

                            event,

                            index

                        )=>

                        (

                            <tr

                                key={

                                    index

                                }

                            >

                                <td>

                                    {

                                        event.time

                                    }

                                </td>

                                <td>

                                    {

                                        event.prompt

                                    }

                                </td>

                                <td>

                                    {

                                        event.operation

                                    }

                                </td>

                                <td

                                    style={

                                        {

                                            color:

                                            getThreatColor(

                                                event.threat

                                            ),

                                            fontWeight:

                                            "bold"

                                        }

                                    }

                                >

                                    {

                                        event.threat

                                    }

                                </td>

                                <td>

                                    {

                                        event.risk_score

                                    }

                                </td>

                                <td

                                    style={

                                        {

                                            color:

                                            getDecisionColor(

                                                event.decision

                                            ),

                                            fontWeight:

                                            "bold"

                                        }

                                    }

                                >

                                    {

                                        event.decision

                                    }

                                </td>

                            </tr>

                        )

                    )

                }

            </tbody>

        </table>

    );

}

export default AuditTable;