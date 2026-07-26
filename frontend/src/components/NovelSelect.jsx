import { AutoComplete } from "antd";

export default function NovelSelect({ novels, value, onChange, disabled }) {
  const options = (novels || []).map((n) => ({
    value: n.title,
    label: n.author ? `${n.title} · ${n.author}` : n.title,
  }));

  return (
    <AutoComplete
      allowClear
      options={options}
      style={{ width: "100%" }}
      placeholder="소설을 선택하거나 제목을 입력하세요"
      filterOption={(input, option) =>
        (option?.value || "").toLowerCase().includes(input.toLowerCase())
      }
      value={value}
      onChange={onChange}
      disabled={disabled}
    />
  );
}
