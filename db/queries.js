const Pool = require('pg').Pool;

const pool = new Pool({
  user: 'result',
  host: 'localhost',
  database: 'results',
  password: 'result123',
  port: 5432,
})

const insertData = (req, res) => {
    let message = '';
    const { studentInfo, tableData, summary } = req.body;
    const { CRN, name,level,campus,programme, yearpart, examRollNo} = studentInfo;
    const { date, grandTotal, result } = summary;
    const subjectData = { "tableData":tableData };

    ;(async () => {
        const client = await pool.connect()
        try {
          const response = await client.query('SELECT * FROM student WHERE crn = $1', [CRN])
          if(!response.rows[0]){
            client.query('INSERT INTO student (crn, name,level,campus,programme) VALUES ($1, $2, $3, $4, $5)',
            [CRN, name,level,campus,programme],
            (error,results) => {
                if(error)
                    throw error;
                message = `Student added with CRN: ${CRN}. `
        })
        }
        client.query('INSERT INTO marksheet (yearpart, examRoll, crn, subjectData, date, grandTotal, result) VALUES ($1, $2, $3, $4, $5, $6, $7)',
        [yearpart, examRollNo, CRN, subjectData, date, grandTotal, result],
        (error,results) => {
            if(error)
                throw error;
            res.status(201).send(`${message}\nMarksheet added of student with CRN: ${CRN}.`);
        }
    )

        } finally {
          // Make sure to release the client before any error handling,
          // just in case the error handling itself throws an error.
          client.release()
        }
      })().catch(err => console.log(err.stack));

}

const showData = (req, res) => {
    pool.query('SELECT * FROM student S INNER JOIN marksheet M ON S.crn=M.crn',  (error, results) => {
        if (error) {
          throw error;
        }
        res.status(200).json(results.rows)
    })
}

module.exports = {
    insertData,
    showData
}