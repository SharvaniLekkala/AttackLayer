function MetricCard({

    title,

    value

}){

    return(

        <div

            className=

            "metric-card"

        >

            <h3>

                {

                    title

                }

            </h3>

            <div

                className=

                "metric-divider"

            >

            </div>

            <h2>

                {

                    value===undefined

                    ||

                    value===null

                    ?

                    "-"

                    :

                    value

                }

            </h2>

        </div>

    );

}

export default MetricCard;