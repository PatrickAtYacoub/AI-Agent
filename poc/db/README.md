# Installation

```
pip install phidata
```

# Setup

```
CREATE TABLE produkte (
    product_number SERIAL PRIMARY KEY,
    input_voltage INT,
    input_current INT,
    output_voltage INT,
    output_current INT,
    number_io_ports INT,
    bus_protocol VARCHAR(100)
);

```
