function StatusCard({

    title,

    value

}) {

    return (

        <div

            className="status-card"

        >

            <h3>

                {title}

            </h3>

            <p>

                {value}

            </p>

        </div>

    );

}

export default StatusCard;