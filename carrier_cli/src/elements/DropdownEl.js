import React, { useState } from 'react';
import { Dropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

const DropdownEl = (props) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggle = () => setDropdownOpen(prevState => !prevState);

  //Zmiana funkcji tak aby szedł dobry post i przyjęcie tego w api, operuje na id wiersza i tokenie
  const send_post_request = (index_of_row, all_packages, state) => {
    // let path = 'https://murmuring-springs-10121.herokuapp.com/root/carrier/dashboard'
    // axios.post(path, {
    //   params: {
    //     "cookie": token
    //   }
    // }).then(resp => {
    //   if (resp.data.data.is_authorized)
    //     this.setState({ "all_packages": resp.data.data.all_packages })
    //   else
    //     this.is_authorized = false
    // })

  }

  return (
    <Dropdown isOpen={dropdownOpen} toggle={toggle}>
      <DropdownToggle caret>
        Wybór statusu
        </DropdownToggle>
      <DropdownMenu>
        <DropdownItem>
          <div onClick={()=>props.send_post_request("Nadana", props.index_of_row, props.username)}>
            Nadana
          </div>
        </DropdownItem>
        <DropdownItem>
        <div onClick={()=>props.send_post_request("W drodze", props.index_of_row, props.username)}>
            W drodze
          </div>
        </DropdownItem>
        <DropdownItem>
          <div onClick={()=>props.send_post_request("Dostarczona", props.index_of_row, props.username)}>
            Dostarczona
          </div>
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  );
}

export default DropdownEl;