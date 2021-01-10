import {useAuth0} from '@auth0/auth0-react';


const CreateToken = (props) => {
    const {user} = useAuth0();
    var user_info = JSON.stringify(user, null, 2)
    //var login = user_info.email
    var string = "działa"
    props.cosiek(string)
}

export default CreateToken
