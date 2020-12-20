import React, { useState } from 'react';
import { Dropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

const DropdownEl = (props) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggle = () => setDropdownOpen(prevState => !prevState);
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