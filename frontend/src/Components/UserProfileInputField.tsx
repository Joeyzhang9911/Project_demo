import { OutlinedInput } from "@mui/material";

interface InputFieldFeatures {
    name: string;
    value: string;
    editing?: boolean;
    onChange: React.ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement>;
    noDefault?: boolean;
  }
  
  const InputField = ({ name, value, editing, onChange, noDefault } : InputFieldFeatures) => {
    return (
      <>
        <h3>{name}</h3>
        { noDefault ?
          <OutlinedInput
            id="outlined-adornment-weight"
            value={value}
            fullWidth
            sx={{
                backgroundColor: 'white'
            }}
            disabled={!editing}
            onChange={onChange}
          /> :
          <OutlinedInput
            id="outlined-adornment-weight"
            defaultValue={value}
            fullWidth
            sx={{
                backgroundColor: 'white'
            }}
            disabled={!editing}
            onChange={onChange}
          />
        }
      </>
    );
  };
  
  export default InputField;
  