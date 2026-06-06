function MemoryTable({

    memories

}){

    function getStatusColor(

        status

    ){

        if(

            status===

            "ACTIVE"

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

                        ID

                    </th>

                    <th>

                        Memory

                    </th>

                    <th>

                        Category

                    </th>

                    <th>

                        Trust

                    </th>

                    <th>

                        Risk

                    </th>

                    <th>

                        Version

                    </th>

                    <th>

                        Status

                    </th>

                    <th>

                        Source

                    </th>

                </tr>

            </thead>

            <tbody>

                {

                    memories.length===0

                    ?

                    <tr>

                        <td

                            colSpan="8"

                        >

                            No memories

                        </td>

                    </tr>

                    :

                    memories.map(

                        (

                            memory

                        )=>

                        (

                            <tr

                                key={

                                    memory.id

                                }

                            >

                                <td>

                                    {

                                        memory.id

                                    }

                                </td>

                                <td>

                                    {

                                        memory.fact

                                    }

                                </td>

                                <td>

                                    {

                                        memory.category

                                    }

                                </td>

                                <td>

                                    {

                                        memory.trust_score

                                    }

                                </td>

                                <td>

                                    {

                                        memory.risk_score

                                    }

                                </td>

                                <td>

                                    {

                                        memory.version

                                    }

                                </td>

                                <td

                                    style={

                                        {

                                            color:

                                            getStatusColor(

                                                memory.status

                                            ),

                                            fontWeight:

                                            "bold"

                                        }

                                    }

                                >

                                    {

                                        memory.status

                                    }

                                </td>

                                <td>

                                    {

                                        memory.source

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

export default MemoryTable;